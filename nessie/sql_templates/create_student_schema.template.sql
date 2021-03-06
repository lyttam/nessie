/**
 * Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.
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

CREATE SCHEMA IF NOT EXISTS {redshift_schema_student};

CREATE TABLE IF NOT EXISTS {redshift_schema_student}.canvas_api_enrollments
(
    course_id VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    last_activity_at TIMESTAMP,
    feed VARCHAR(max) NOT NULL
)
DISTKEY(course_id)
SORTKEY(course_id);

CREATE TABLE IF NOT EXISTS {redshift_schema_student}.sis_api_degree_progress
(
    sid VARCHAR NOT NULL,
    feed VARCHAR(max) NOT NULL
)
DISTKEY(sid)
SORTKEY(sid);

CREATE TABLE IF NOT EXISTS {redshift_schema_student}.sis_api_drops_and_midterms
(
    sid VARCHAR NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    feed VARCHAR(max) NOT NULL
)
DISTKEY(sid)
SORTKEY(sid, term_id);

CREATE TABLE IF NOT EXISTS {redshift_schema_student}.sis_api_profiles
(
    sid VARCHAR NOT NULL,
    feed VARCHAR(max) NOT NULL
)
DISTKEY(sid)
SORTKEY(sid);

CREATE TABLE IF NOT EXISTS {redshift_schema_student}.student_profiles
(
    sid VARCHAR NOT NULL,
    profile VARCHAR(max) NOT NULL
)
DISTKEY (sid)
SORTKEY (sid);

CREATE TABLE IF NOT EXISTS {redshift_schema_student}.student_academic_status
(
    sid VARCHAR NOT NULL,
    uid VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    level VARCHAR(2),
    gpa DECIMAL(4,3),
    units DECIMAL (4,1)
)
DISTKEY (units)
INTERLEAVED SORTKEY (sid, last_name, level, gpa, units, uid, first_name);

CREATE TABLE IF NOT EXISTS {redshift_schema_student}.student_holds
(
    sid VARCHAR NOT NULL,
    feed VARCHAR(max) NOT NULL
)
DISTKEY (sid)
SORTKEY (sid);

CREATE TABLE IF NOT EXISTS {redshift_schema_student}.student_majors
(
    sid VARCHAR NOT NULL,
    major VARCHAR NOT NULL
)
DISTKEY (major)
SORTKEY (major);

CREATE TABLE IF NOT EXISTS {redshift_schema_student}.student_enrollment_terms
(
    sid VARCHAR NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    enrollment_term VARCHAR(max) NOT NULL
)
DISTKEY (sid)
SORTKEY (sid, term_id);

CREATE TABLE IF NOT EXISTS {redshift_schema_student}.student_term_gpas
(
    sid VARCHAR NOT NULL,
    term_id VARCHAR(4) NOT NULL,
    gpa DECIMAL(4,3),
    units_taken_for_gpa DECIMAL(4,1)
)
DISTKEY (sid)
SORTKEY (sid, term_id);
