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

from flask import current_app as app
from nessie.externals import redshift, s3
from nessie.jobs.background_job import BackgroundJob
from nessie.lib.util import get_s3_canvas_api_path

"""Logic for Canvas API schema verification job."""


class VerifyCanvasApiImport(BackgroundJob):

    canvas_schema = app.config['REDSHIFT_SCHEMA_CANVAS']
    canvas_api_schema = app.config['REDSHIFT_SCHEMA_CANVAS_API_INTERNAL']

    def run(self):
        app.logger.info('Starting Canvas API import verification job...')
        expected_courses = self.get_expected_courses()

        gradebook_history_result = self.verify_import('gradebook_history', expected_courses)
        # gradebook_history_result = self.verify_s3('gradebook_history', expected_courses)
        # gradebook_history_result = ''

        grade_change_log_result = self.verify_import('grade_change_log', expected_courses)
        # grade_change_log_result = self.verify_s3('grade_change_log', expected_courses)

        return f"""Verified Canvas API imports for {len(expected_courses)} courses.
                {gradebook_history_result}
                {grade_change_log_result}"""

    def get_expected_courses(self):
        results = redshift.fetch(
            f"""SELECT course.canvas_id AS course_id, count(DISTINCT sub.assignment_id) AS assignment_count
            FROM {self.canvas_schema}.enrollment_term_dim term
            JOIN {self.canvas_schema}.course_dim course ON term.id = course.enrollment_term_id
            JOIN {self.canvas_schema}.assignment_dim assign ON course.id = assign.course_id
            JOIN {self.canvas_schema}.submission_dim sub
              ON assign.id = sub.assignment_id
              AND sub.grade_state <> 'not_graded'
            WHERE term.name IN ('Spring 2020')
            GROUP BY course.canvas_id
            ORDER BY course.canvas_id""",
        )
        return {r['course_id']: r['assignment_count'] for r in results}

    def verify_import(self, table_name, expected_courses):
        app.logger.info(f'Verifying {table_name} assignment counts for {len(expected_courses)} courses.')
        result = {
            'success': [],
            'fail': [],
            'no_data': [],
        }
        imported_courses = self.get_imported_courses(table_name)
        for course_id, expected_assignment_count in expected_courses.items():
            imported_assignment_count = imported_courses.get(course_id, 0)
            if expected_assignment_count == 0:
                result['no_data'].append(str(course_id))
            elif imported_assignment_count >= expected_assignment_count:
                result['success'].append(str(course_id))
            else:
                result['fail'].append(str(course_id))

        app.logger.info(f"""Verified {table_name} import is complete for {len(result['success'])} of {len(expected_courses)} courses.
                        {len(result['no_data'])} courses have no graded assignments.
                        Missing data for {len(result['fail'])} courses.""")
        if len(result['fail']):
            failed_course_ids = ','.join(result['fail'])
            app.logger.warn(f"""{table_name} assignment counts do not match for courses {failed_course_ids}""")
            # self.audit_assignments(table_name, course_ids=result['fail'])
        return {table_name: {status: len(courses) for status, courses in result.items()}}

    def get_imported_courses(self, table_name):
        query = f"""SELECT course_id, count(DISTINCT assignment_id) AS assignment_count
                FROM {self.canvas_api_schema}.{table_name}
                GROUP BY course_id
                ORDER BY course_id"""
        results = redshift.fetch(query)
        return {r['course_id']: r['assignment_count'] for r in results}

    def audit_assignments(self, table_name, course_ids):
        app.logger.info(f'Investigating {table_name} assignment count mismatch for {len(course_ids)} courses.')
        results = {}
        for course_id in course_ids:
            imported = self.get_imported_assignments(table_name, course_id)
            expected = self.get_expected_assignments(course_id)
            missing = expected - imported
            extra = imported - expected
            if len(missing) or len(extra):
                results[course_id] = {
                    'missing_assignments': missing,
                    'unexpected_assignments': extra,
                }
        app.logger.info(f"""Audit result: {results}""")

    def get_expected_assignments(self, course_id):
        results = redshift.fetch(
            f"""SELECT DISTINCT assign.canvas_id AS assignment_id
            FROM {self.canvas_schema}.course_dim course
            JOIN {self.canvas_schema}.assignment_dim assign ON course.id = assign.course_id
            JOIN {self.canvas_schema}.submission_dim sub ON assign.id = sub.assignment_id
            WHERE course.canvas_id=%s
            AND sub.graded_at IS NOT NULL""",
            params=(course_id,),
        )
        return set([r['assignment_id'] for r in results])

    def get_imported_assignments(self, table_name, course_id):
        results = redshift.fetch(
            f"""SELECT DISTINCT assignment_id
                FROM {self.canvas_api_schema}.{table_name}
                WHERE course_id=%s""",
            params=(course_id,),
        )
        return set([int(r['assignment_id']) for r in results])

    def verify_s3(self, table_name, expected_courses):
        app.logger.info(f'Verifying {table_name} s3 keys for {len(expected_courses)} courses.')
        s3_course_ids = self.get_s3_course_ids(table_name)
        result = {
            'success': [],
            'fail': [],
            'no_data': [],
        }
        for course_id, expected_assignment_count in expected_courses.items():
            if expected_assignment_count == 0:
                result['no_data'].append(str(course_id))
            elif course_id in s3_course_ids:
                result['success'].append(str(course_id))
            else:
                result['fail'].append(str(course_id))

        app.logger.info(f"""Verified {table_name} S3 keys exist for {len(result['success'])} of {len(expected_courses)} courses.
                        {len(result['no_data'])} courses have no graded assignments.
                        Missing S3 keys for {len(result['fail'])} courses.""")
        if len(result['fail']):
            failed_course_ids = ','.join(result['fail'])
            app.logger.warn(f'Failed to import {table_name} for course IDs {failed_course_ids}')
        return {table_name: {status: len(courses) for status, courses in result.items()}}

    def get_s3_course_ids(self, table_name):
        # s3_keys = s3.get_keys_with_prefix(f'{get_s3_canvas_api_path()}/gradebook_history/gradebook_history')
        s3_keys = s3.get_keys_with_prefix(f'canvas-api/lambda/transformed/{table_name}/{table_name}', bucket='la-nessie-transient')
        course_ids = []
        for key in s3_keys:
            file_name = key.split('/')[-1]
            course_id = int(file_name.split('_')[-2])
            course_ids.append(course_id)
        return sorted(set(course_ids))
