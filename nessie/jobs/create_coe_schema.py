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

from itertools import groupby
import json
import operator

from flask import current_app as app
from nessie.externals import redshift, s3
from nessie.jobs.background_job import BackgroundJob, verify_external_schema
from nessie.lib.util import get_s3_coe_daily_path, resolve_sql_template, resolve_sql_template_string
import psycopg2


"""Logic for COE schema creation job."""


external_schema = app.config['REDSHIFT_SCHEMA_COE_EXTERNAL']
internal_schema = app.config['REDSHIFT_SCHEMA_COE']
internal_schema_identifier = psycopg2.sql.Identifier(internal_schema)


class CreateCoeSchema(BackgroundJob):

    def run(self):
        app.logger.info(f'Starting COE schema creation job...')
        redshift.drop_external_schema(external_schema)
        resolved_ddl = resolve_sql_template('create_coe_schema.template.sql')
        # TODO This DDL drops and recreates the internal schema before the external schema is verified. We
        # ought to set up proper staging in conjunction with verification. It's also possible that a persistent
        # external schema isn't needed.
        if redshift.execute_ddl_script(resolved_ddl):
            app.logger.info(f'COE external schema created.')
            if not verify_external_schema(external_schema, resolved_ddl):
                return False
        else:
            app.logger.error(f'COE external schema creation failed.')
            return False
        coe_rows = redshift.fetch(
            'SELECT * FROM {schema}.students ORDER by sid',
            schema=internal_schema_identifier,
        )

        profile_rows = []
        index = 1
        for sid, rows_for_student in groupby(coe_rows, operator.itemgetter('sid')):
            app.logger.info(f'Generating COE profile for SID {sid} ({index} of {len(coe_rows)})')
            index += 1
            row_for_student = list(rows_for_student)[0]
            # TODO More COE-specific attributes will get merged into this profile as we receive them.
            coe_profile = {
                'advisorUid': row_for_student.get('advisor_ldap_uid'),
            }
            profile_rows.append('\t'.join([str(sid), json.dumps(coe_profile)]))

        s3_key = f'{get_s3_coe_daily_path()}/coe_profiles.tsv'
        app.logger.info(f'Will stash {len(profile_rows)} feeds in S3: {s3_key}')
        if not s3.upload_data('\n'.join(profile_rows), s3_key):
            app.logger.error('Error on S3 upload: aborting job.')
            return False

        app.logger.info('Will copy S3 feeds into Redshift...')
        query = resolve_sql_template_string(
            """
            COPY {redshift_schema_coe}.student_profiles
                FROM '{loch_s3_coe_data_path}/coe_profiles.tsv'
                IAM_ROLE '{redshift_iam_role}'
                DELIMITER '\\t';
            VACUUM;
            ANALYZE;
            """,
        )
        if not redshift.execute(query):
            app.logger.error('Error on Redshift copy: aborting job.')
            return False

        return 'COE internal schema created.'
