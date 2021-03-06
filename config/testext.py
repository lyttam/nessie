# Redshift connection parameters.

REDSHIFT_DATABASE = 'database'
REDSHIFT_HOST = 'redshift cluster'
REDSHIFT_PASSWORD = 'password'
REDSHIFT_PORT = 1234
REDSHIFT_USER = 'username'

# Schema names. Since Redshift instances are shared between environments, choose something that can
# be repeatedly created and torn down without conflicts.

REDSHIFT_SCHEMA_ASC = 'testext_mynamehere_asc'
REDSHIFT_SCHEMA_BOAC = 'testext_mynamehere_boac'
REDSHIFT_SCHEMA_CALNET = 'testext_mynamehere_calnet'
REDSHIFT_SCHEMA_CANVAS = 'testext_mynamehere_canvas'
REDSHIFT_SCHEMA_COE = 'testext_mynamehere_coe'
REDSHIFT_SCHEMA_COE_EXTERNAL = 'testext_mynamehere_coe_external'
REDSHIFT_SCHEMA_INTERMEDIATE = 'testext_mynamehere_intermediate'
REDSHIFT_SCHEMA_METADATA = 'testext_mynamehere_metadata'
REDSHIFT_SCHEMA_SIS = 'testext_mynamehere_sis'
REDSHIFT_SCHEMA_SIS_INTERNAL = 'testext_mynamehere_sis_internal'
REDSHIFT_SCHEMA_STUDENT = 'testext_mynamehere_student'

# S3 key prefix. Since the testext bucket is shared between users, choose something unique.

LOCH_S3_PREFIX_TESTEXT = 'mynamehere'
