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

import boto3
from flask import current_app as app

"""Client code to run AWS Lambda operations."""


def get_sts_credentials():
    sts_client = boto3.client('sts')
    role_arn = app.config['AWS_LAMBDA_ROLE_ARN']
    assumed_role_object = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='AssumeAppRoleSession',
        DurationSeconds=900,
    )
    return assumed_role_object['Credentials']


def get_session():
    credentials = get_sts_credentials()
    return boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )


def get_client():
    session = get_session()
    return session.client(
        service_name='lambda',
        region_name=app.config['LOCH_S3_REGION'],
        endpoint_url='https://lambda.{}.amazonaws.com'.format(app.config['LOCH_S3_REGION']),
    )


def invoke(function_name, payload, invocation_type='Event', log_type='None', client_context='None', qualifier='None'):
    client = get_client()
    return client.invoke(
        FunctionName=function_name,
        InvocationType=invocation_type,
        Payload=payload,
    )
