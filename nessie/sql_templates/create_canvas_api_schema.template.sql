/**
 * Copyright ©2020. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

--------------------------------------------------------------------
-- CREATE EXTERNAL SCHEMA
--------------------------------------------------------------------

CREATE EXTERNAL SCHEMA {redshift_schema_canvas_api}
FROM data catalog
DATABASE '{redshift_schema_canvas_api}'
IAM_ROLE '{redshift_iam_role}'
CREATE EXTERNAL DATABASE IF NOT EXISTS;

--------------------------------------------------------------------
-- External Tables
--------------------------------------------------------------------

CREATE EXTERNAL TABLE {redshift_schema_canvas_api}.gradebook_history (
    id BIGINT,
    course_id BIGINT,
    assignment_id BIGINT,
    assignment_name VARCHAR,
    attempt INT,
    body TEXT,
    cached_due_date TIMESTAMP,
    current_grade VARCHAR,
    current_graded_at TIMESTAMP,
    current_grader VARCHAR,
    entered_grade VARCHAR,
    entered_score DOUBLE PRECISION,
    excused BOOLEAN,
    external_tool_url VARCHAR(MAX),
    extra_attempts VARCHAR,
    grade_matches_current_submission BOOLEAN,
    grade VARCHAR,
    graded_at TIMESTAMP,
    grader_id BIGINT,
    grader VARCHAR,
    grading_period_id VARCHAR,
    late_policy_status VARCHAR,
    late BOOLEAN,
    missing BOOLEAN,
    points_deducted DOUBLE PRECISION,
    posted_at TIMESTAMP,
    preview_url VARCHAR(MAX),
    score DOUBLE PRECISION,
    seconds_late BIGINT,
    submission_type VARCHAR,
    submitted_at TIMESTAMP,
    url VARCHAR,
    user_id BIGINT,
    user_name VARCHAR,
    workflow_state VARCHAR
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION '{s3_canvas_api_data_path}/gradebook_history';

CREATE EXTERNAL TABLE {redshift_schema_canvas_api}.grade_change_log (
    id BIGINT,
    course_id BIGINT,
    created_at TIMESTAMP,
    event_type VARCHAR,
    excused_after BOOLEAN,
    excused_before BOOLEAN,
    grade_after VARCHAR,
    grade_before VARCHAR,
    graded_anonymously BOOLEAN,
    points_possible_after DOUBLE PRECISION,
    points_possible_before DOUBLE PRECISION,
    version_number INT,
    links STRUCT <
        assignment:BIGINT,
        course:BIGINT,
        student:VARCHAR,
        grader:VARCHAR,
        page_view:VARCHAR
    >
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION '{s3_canvas_api_data_path}/grade_change_log';

--------------------------------------------------------------------
-- Internal schema
--------------------------------------------------------------------

DROP SCHEMA IF EXISTS {redshift_schema_canvas_api_internal} CASCADE;
CREATE SCHEMA {redshift_schema_canvas_api_internal};

--------------------------------------------------------------------
-- Internal tables
--------------------------------------------------------------------

CREATE TABLE {redshift_schema_canvas_api_internal}.gradebook_history
SORTKEY (course_id, assignment_id)
AS (
    SELECT
        id, course_id, assignment_id, assignment_name,  attempt, body,
        cached_due_date, current_grade, current_graded_at, current_grader,
        entered_grade, entered_score, excused, external_tool_url, extra_attempts,
        grade_matches_current_submission, grade, graded_at, grader_id, grader,
        grading_period_id, late_policy_status, late, missing, points_deducted,
        posted_at, preview_url, score, seconds_late, submission_type, submitted_at,
        url, user_id, user_name, workflow_state
    FROM {redshift_schema_canvas_api}.gradebook_history
);

CREATE TABLE {redshift_schema_canvas_api_internal}.grade_change_log
SORTKEY (course_id, assignment_id)
AS (
    SELECT
        id, course_id, links.assignment AS assignment_id, created_at, event_type,
        excused_after, excused_before, grade_after, grade_before, graded_anonymously,
        points_possible_after, points_possible_before, version_number
    FROM {redshift_schema_canvas_api}.grade_change_log
);
