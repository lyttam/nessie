"""
Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.

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


import json

from flask import current_app as app
from nessie.externals import lambda_, s3
from nessie.jobs.background_job import BackgroundJob


"""Logic for transforming Canvas API data into Spark-parsable JSON."""


class TransformCanvasApiData(BackgroundJob):

    def run(self, table_name, course_id_prefix):
        app.logger.info('Starting Canvas API data transform job...')

        dest_path = 'canvas-api/lambda/transformed'
        source_prefix = f'canvas-api-data/incremental-annetest/{table_name}/{table_name}_{course_id_prefix}'
        keys = s3.get_keys_with_prefix(source_prefix)

        app.logger.info(f'Will invoke lambda on {len(keys)} objects from {source_prefix} and put results to {dest_path}.')
        for key in keys:
            self.invoke_transform(key, dest_path)

        return 'Canvas API data transform complete.'

    def invoke_transform(self, source_key, dest_path):
        payload = {
            'trigger': 'nessie',
            'source': {
                'bucket': app.config['LOCH_S3_BUCKET'],
                'key': source_key,
            },
            'dest': {
                'bucket': app.config['LRS_CANVAS_INCREMENTAL_TRANSIENT_BUCKET'],
                'path': dest_path,
            },
        }
        response = lambda_.invoke('canvas-api-transform', json.dumps(payload).encode())
        if int(response.get('StatusCode')) >= 400:
            app.logger.warn(f'Error response from lambda: {response}')
        else:
            app.logger.info(f'Lambda successfully invoked on {source_key}')
