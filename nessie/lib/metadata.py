"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""


from datetime import datetime
import os

from flask import current_app as app
from nessie.externals import redshift, s3
from nessie.lib.util import get_s3_sis_api_daily_path, resolve_sql_template_string
import psycopg2.sql


def create_canvas_sync_status(job_id, filename, canvas_table, source_url):
    sql = """INSERT INTO {schema}.canvas_sync_job_status
               (job_id, filename, canvas_table, source_url, status, instance_id, created_at, updated_at)
               VALUES (%s, %s, %s, %s, 'created', %s, current_timestamp, current_timestamp)
               """
    return redshift.execute(
        sql,
        params=(job_id, filename, canvas_table, source_url, _instance_id()),
        schema=_schema(),
    )


def get_failures_from_last_sync():
    last_job_id = None
    failures = []

    job_id_result = redshift.fetch(
        """SELECT MAX(job_id) AS last_job_id FROM {schema}.canvas_sync_job_status WHERE job_id LIKE %s""",
        params=['sync%%'],
        schema=_schema(),
    )
    if not job_id_result:
        app.logger.error('Failed to retrieve id for last sync job')
    else:
        last_job_id = job_id_result[0]['last_job_id']
        failures_query = """SELECT * FROM {schema}.canvas_sync_job_status WHERE job_id = %s
            AND (status NOT IN ('complete', 'duplicate') OR destination_size != source_size)"""
        failures = redshift.fetch(failures_query, params=[last_job_id], schema=_schema())
    return {'job_id': last_job_id, 'failures': failures}


def update_canvas_sync_status(job_id, key, status, **kwargs):
    filename = key.split('/')[-1]
    destination_url = s3.build_s3_url(key, credentials=False)

    sql = """UPDATE {schema}.canvas_sync_job_status
             SET destination_url=%s, status=%s, updated_at=current_timestamp"""
    params = [destination_url, status]
    for key in ['details', 'source_size', 'destination_size']:
        if kwargs.get(key):
            sql += f', {key}=%s'
            params.append(kwargs[key])
    sql += ' WHERE job_id=%s AND filename=%s'
    params += [job_id, filename]

    return redshift.execute(
        sql,
        params=tuple(params),
        schema=_schema(),
    )


def create_canvas_snapshot(key, size):
    canvas_table, filename = key.split('/')[-2:]
    url = s3.build_s3_url(key, credentials=False)
    sql = """INSERT INTO {schema}.canvas_synced_snapshots
             (filename, canvas_table, url, size, created_at)
             VALUES (%s, %s, %s, %s, current_timestamp)"""
    return redshift.execute(
        sql,
        params=(filename, canvas_table, url, size),
        schema=_schema(),
    )


def delete_canvas_snapshots(keys):
    filenames = [key.split('/')[-1] for key in keys]
    sql = 'UPDATE {schema}.canvas_synced_snapshots SET deleted_at=current_timestamp WHERE filename IN %s'
    return redshift.execute(sql, params=[tuple(filenames)], schema=_schema())


def create_background_job_status(job_id):
    sql = """INSERT INTO {schema}.background_job_status
               (job_id, status, instance_id, created_at, updated_at)
               VALUES (%s, 'started', %s, current_timestamp, current_timestamp)
               """
    return redshift.execute(
        sql,
        params=(job_id, _instance_id()),
        schema=_schema(),
    )


def update_background_job_status(job_id, status, details=None):
    if details:
        details = details[:4096]
    sql = """UPDATE {schema}.background_job_status
             SET status=%s, updated_at=current_timestamp, details=%s
             WHERE job_id=%s"""
    return redshift.execute(
        sql,
        params=(status, details, job_id),
        schema=_schema(),
    )


def update_merged_feed_status(term_id, successes, failures):
    term_id = term_id or 'all'
    redshift.execute(
        'DELETE FROM {schema}.merged_feed_status WHERE sid = ANY(%s) AND term_id = %s',
        schema=_schema(),
        params=((successes + failures), term_id),
    )
    now = datetime.utcnow().isoformat()
    success_records = ['\t'.join([sid, term_id, 'success', now]) for sid in successes]
    failure_records = ['\t'.join([sid, term_id, 'failure', now]) for sid in failures]
    rows = success_records + failure_records
    s3_key = f'{get_s3_sis_api_daily_path()}/merged_feed_status.tsv'
    if not s3.upload_data('\n'.join(rows), s3_key):
        app.logger.error('Error uploading merged feed status updates to S3.')
        return
    query = resolve_sql_template_string(
        """
        COPY {redshift_schema_metadata}.merged_feed_status
            FROM '{loch_s3_sis_api_data_path}/merged_feed_status.tsv'
            IAM_ROLE '{redshift_iam_role}'
            DELIMITER '\\t'
            TIMEFORMAT 'YYYY-MM-DDTHH:MI:SS';
        """
    )
    if not redshift.execute(query):
        app.logger.error('Error copying merged feed status updates to Redshift.')


def _instance_id():
    return os.environ.get('EC2_INSTANCE_ID')


def _schema():
    return psycopg2.sql.Identifier(app.config['REDSHIFT_SCHEMA_METADATA'])
