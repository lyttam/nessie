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

# The test environment mocks the Redshift interface with a local Postgres db.

TESTING = True

LOCH_S3_BUCKET = 'mock-bucket'

REDSHIFT_DATABASE = 'nessie_redshift_test'
REDSHIFT_HOST = 'localhost'
REDSHIFT_PASSWORD = 'nessie'
REDSHIFT_PORT = 5432
REDSHIFT_USER = 'nessie'

REDSHIFT_SCHEMA_ASC = 'asc_test'
REDSHIFT_SCHEMA_BOAC = 'boac_test'
REDSHIFT_SCHEMA_CALNET = 'calnet_test'
REDSHIFT_SCHEMA_CANVAS = 'canvas_test'
REDSHIFT_SCHEMA_COE = 'coe_test'
REDSHIFT_SCHEMA_COE_EXTERNAL = 'coe_external_test'
REDSHIFT_SCHEMA_INTERMEDIATE = 'intermediate_test'
REDSHIFT_SCHEMA_METADATA = 'nessie_metadata_test'
REDSHIFT_SCHEMA_SIS = 'sis_test'
REDSHIFT_SCHEMA_SIS_INTERNAL = 'sis_internal_test'
REDSHIFT_SCHEMA_STUDENT = 'student_test'

SQLALCHEMY_DATABASE_URI = 'postgres://nessie:nessie@localhost:5432/nessie_test'

LOGGING_LOCATION = 'STDOUT'

JOB_SYNC_CANVAS_SNAPSHOTS = {'hour': 1, 'minute': 0}
JOB_RESYNC_CANVAS_SNAPSHOTS = {'hour': 1, 'minute': 40}
JOB_GENERATE_ALL_TABLES = {'hour': 3, 'minute': 30}
