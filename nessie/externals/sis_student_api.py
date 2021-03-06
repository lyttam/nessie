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


"""Official access to student data."""


from flask import current_app as app
from nessie.lib import http
from nessie.lib.mockingbird import fixture


def get_student(cs_id):
    response = _get_student(cs_id)
    if response and hasattr(response, 'json'):
        unwrapped = response.json().get('apiResponse', {}).get('response', {}).get('any', {}).get('students', [])
        if unwrapped:
            unwrapped = unwrapped[0]
        return unwrapped
    else:
        return


@fixture('sis_student_api_{cs_id}')
def _get_student(cs_id, mock=None):
    url = http.build_url(app.config['STUDENT_API_URL'] + '/' + str(cs_id) + '/all')
    with mock(url):
        return authorized_request(url)


def get_term_gpas(cs_id):
    response = _get_registrations(cs_id)
    if response and hasattr(response, 'json'):
        unwrapped = response.json().get('apiResponse', {}).get('response', {}).get('any', {}).get('registrations', [])
        term_gpas = {}
        for registration in unwrapped:
            # Ignore terms in which the student was not an undergraduate.
            if registration.get('academicCareer', {}).get('code') != 'UGRD':
                continue
            # Ignore terms in which the student took no classes with units. These may include future terms.
            total_units = next((u for u in registration.get('termUnits', []) if u['type']['code'] == 'Total'), None)
            if not total_units or not total_units.get('unitsTaken'):
                continue
            term_id = registration.get('term', {}).get('id')
            gpa = registration.get('termGPA', {}).get('average')
            term_units = registration.get('termUnits', [])
            units_taken_for_gpa = next((tu['unitsTaken'] for tu in term_units if tu['type']['code'] == 'For GPA'), None)
            if term_id and gpa is not None:
                term_gpas[term_id] = {
                    'gpa': gpa,
                    'unitsTakenForGpa': units_taken_for_gpa,
                }
        return term_gpas
    else:
        return


@fixture('sis_registrations_api_{cs_id}')
def _get_registrations(cs_id, mock=None):
    url = http.build_url(app.config['STUDENT_API_URL'] + '/' + str(cs_id) + '/registrations')
    with mock(url):
        return authorized_request(url)


def authorized_request(url):
    auth_headers = {
        'app_id': app.config['STUDENT_API_ID'],
        'app_key': app.config['STUDENT_API_KEY'],
        'Accept': 'application/json',
    }
    return http.request(url, auth_headers)
