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

from time import sleep

from flask import current_app as app
from nessie.externals import glue, s3
from nessie.jobs.background_job import BackgroundJob, BackgroundJobError
from nessie.lib.util import get_s3_canvas_api_path

"""Logic for running a Glue job."""


class RunGlueJob(BackgroundJob):

    def run(self, glue_job_name):
        self.transient_bucket = app.config['LRS_CANVAS_INCREMENTAL_TRANSIENT_BUCKET']
        self.glue_role = app.config['LRS_GLUE_SERVICE_ROLE']

        app.logger.info('Starting Glue job...')
        response = self.start_job(glue_job_name)

        # TODO: Add logic to write glue job details to metadata table.
        return f'Glue job {glue_job_name} completed. JobRun={response}'

    def start_job(self, job_name):
        job_arguments = {
            '--LRS_INCREMENTAL_TRANSIENT_BUCKET': app.config['LRS_CANVAS_INCREMENTAL_TRANSIENT_BUCKET'],
            '--CANVAS_API_SCHEMA_PATH': app.config['CANVAS_API_GLUE_SCHEMA_PATH'],
            '--CANVAS_API_INPUT_DATA_PATH': get_s3_canvas_api_path(transformed=True),
            '--LOCH_S3_BUCKET': app.config['LOCH_S3_BUCKET'],
            '--job-bookmark-option': 'job-bookmark-disable',
        }

        response = glue.start_glue_job(
            job_name, job_arguments,
            app.config['LRS_CANVAS_GLUE_JOB_CAPACITY'],
            app.config['LRS_CANVAS_GLUE_JOB_TIMEOUT'],
        )
        if not response:
            raise BackgroundJobError('Failed to create Glue job')
        elif 'JobRunId' in response:
            job_run_id = response['JobRunId']
            app.logger.debug(f'Response : {response}')
            app.logger.info('Started job run successfully for the Job Name {} with Job Run id {}'.format(job_name, job_run_id))

            # Once the Caliper glue job is started successfully poll the job run every 30 seconds to get the status of the run
            while True:
                status = glue.check_job_run_status(job_name, job_run_id)
                if not status:
                    raise BackgroundJobError('Failed to check Glue job status')
                elif status['JobRun']['JobRunState'] == 'SUCCEEDED':
                    app.logger.info(f'Glue job {job_name} completed successfully: {status}')
                    break
                elif status['JobRun']['JobRunState'] == 'FAILED' or status['JobRun']['JobRunState'] == 'TIMEOUT':
                    raise BackgroundJobError(f'Glue job {job_name} failed or timed out: {status}')

                sleep(30)
            return status
        return response
