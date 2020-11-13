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


AWS_APP_ROLE_ARN = '<app_role_arn>'
AWS_LAMBDA_ROLE_ARN = '<lambda_role_arn>'

# Redshift connection parameters.

RDS_APP_BOA_USER = 'boa_rds_username'
REDSHIFT_APP_BOA_USER = 'boa_redshift_username'

REDSHIFT_DATABASE = 'database'
REDSHIFT_HOST = 'redshift cluster'
REDSHIFT_PASSWORD = 'password'
REDSHIFT_PORT = 1234
REDSHIFT_USER = 'username'

# Schema names. Since Redshift instances are shared between environments, choose something that can
# be repeatedly created and torn down without conflicts.

REDSHIFT_SCHEMA_ADVISOR = 'testext_mynamehere_boac_advisor_external'
REDSHIFT_SCHEMA_ADVISOR_INTERNAL = 'testext_mynamehere_boac_advisor'
REDSHIFT_SCHEMA_ASC = 'testext_mynamehere_asc'
REDSHIFT_SCHEMA_ASC_ADVISING_NOTES = 'testext_mynamehere_asc_advising_notes_external'
REDSHIFT_SCHEMA_ASC_ADVISING_NOTES_INTERNAL = 'testext_mynamehere_asc_advising_notes'
REDSHIFT_SCHEMA_BOAC = 'testext_mynamehere_boac'
REDSHIFT_SCHEMA_CALNET = 'testext_mynamehere_calnet'
REDSHIFT_SCHEMA_CANVAS = 'testext_mynamehere_canvas'
REDSHIFT_SCHEMA_COE = 'testext_mynamehere_coe'
REDSHIFT_SCHEMA_COE_EXTERNAL = 'testext_mynamehere_coe_external'
REDSHIFT_SCHEMA_DATA_SCIENCE_ADVISING = 'testext_mynamehere_data_science_advising_external'
REDSHIFT_SCHEMA_DATA_SCIENCE_ADVISING_INTERNAL = 'testext_mynamehere_data_science_advising'
REDSHIFT_SCHEMA_E_I_ADVISING_NOTES = 'testext_mynamehere_e_i_advising_notes_external'
REDSHIFT_SCHEMA_E_I_ADVISING_NOTES_INTERNAL = 'testext_mynamehere_e_i_advising_notes'
REDSHIFT_SCHEMA_INTERMEDIATE = 'testext_mynamehere_intermediate'
REDSHIFT_SCHEMA_SIS = 'testext_mynamehere_sis'
REDSHIFT_SCHEMA_SIS_ADVISING_NOTES = 'testext_mynamehere_sis_advising_notes_external'
REDSHIFT_SCHEMA_SIS_ADVISING_NOTES_INTERNAL = 'testext_mynamehere_sis_advising_notes'
REDSHIFT_SCHEMA_SIS_INTERNAL = 'testext_mynamehere_sis_internal'
REDSHIFT_SCHEMA_SIS_TERMS = 'testext_mynamehere_sis_terms'
REDSHIFT_SCHEMA_STUDENT = 'testext_mynamehere_student'

# S3 key prefix. Since the testext bucket is shared between users, choose something unique.

LOCH_S3_PREFIX_TESTEXT = 'mynamehere'
