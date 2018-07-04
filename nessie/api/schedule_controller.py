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


from flask import current_app as app, request
from nessie.api.auth_helper import auth_required
from nessie.api.errors import BadRequestError
from nessie.jobs.scheduling import get_scheduler, PG_ADVISORY_LOCK_IDS
from nessie.lib.http import tolerant_jsonify
from nessie.models.util import get_granted_lock_ids


def job_to_dict(job):
    lock_ids = get_granted_lock_ids()
    job_components = job.args[0]
    if not hasattr(job_components, '__iter__'):
        job_components = [job_components]
    return {
        'id': job.id.lower(),
        'components': [c.__name__ for c in job_components],
        'trigger': str(job.trigger),
        'nextRun': str(job.next_run_time) if job.next_run_time else None,
        'locked': (PG_ADVISORY_LOCK_IDS.get(job.id) in lock_ids),
    }


@app.route('/api/schedule', methods=['GET'])
def get_job_schedule():
    sched = get_scheduler()
    return tolerant_jsonify([job_to_dict(job) for job in sched.get_jobs()])


@app.route('/api/schedule/<job_id>', methods=['POST'])
@auth_required
def update_job_schedule(job_id):
    try:
        args = request.get_json(force=True)
    except Exception as e:
        raise BadRequestError(str(e))
    sched = get_scheduler()
    job_id = job_id.upper()
    job = sched.get_job(job_id)
    if not job:
        raise BadRequestError(f'No job found for job id: {job_id}')
    # If JSON properties are present, they will be evaluated by APScheduler's cron trigger API.
    # https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html#module-apscheduler.triggers.cron
    if args:
        try:
            job.reschedule(trigger='cron', **args)
        except Exception as e:
            raise BadRequestError(f'Error rescheduling job: {e}')
    # Passing a empty JSON object will pause this job.
    else:
        job.pause()
    job = sched.get_job(job_id)
    return tolerant_jsonify(job_to_dict(job))