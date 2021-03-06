# -*- coding=utf-8 -*-
"""
Contains code for how to connect to the different Onadata endpoints
"""

import logging
import os
import uuid

from requests.auth import AuthBase
from statsd import StatsClient, TCPStatsClient

import graphite

logger = logging.getLogger(__name__)  # pylint: disable=C0103
statsd = StatsClient(
    host=os.environ.get('STATSD_HOST', '127.0.0.1'),
    port=os.environ.get('STATSD_PORT', 8125),
    prefix=os.environ.get('STATSD_PREFIX', 'locust'))  # pylint: disable=C0103


# pylint: disable=R0903
class TempTokenAuth(AuthBase):
    """
    TempToken Authorization class.

    Adds "Authorization" header with "TempToken [token]" to a request.
    """

    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers['Authorization'] = 'TempToken %s' % self.token

        return request


def api_path(endpoint, root_path='/api/v1/'):
    """
    Returns the API endpoint by appending the endpoint to the root_path.
    """
    return root_path + endpoint + '.json'


def login(user):
    """
    Login to API.
    """
    with statsd.timer('user_time'):
        response = user.client.get(
            api_path('user'), auth=user.auth, name='/user')
        statsd.incr('user_%s' % response.status_code)
        if response.status_code == 200:
            user.temp_token = response.json().get('temp_token')
            user.username = response.json().get('username')
            user.auth = TempTokenAuth(user.temp_token) \
                if hasattr(user, 'temp_token') else None
        else:
            logger.info(response.content)
    statsd.incr('user_no_requests')
    statsd.incr('no_requests')


def user_profile(user):
    """
    Get user profile.
    """
    if not user.username:
        login(user)
    with statsd.timer('profiles_time'):
        response = user.client.get(
            api_path('profiles/' + user.username),
            auth=user.auth,
            name='/profiles/[username]')
        statsd.incr('profiles_%s' % response.status_code)
    statsd.incr('profiles_no_requests')
    statsd.incr('no_requests')


def orgs_shared_with(user):
    """
    Orgs endpoint for orgs shared with the user.
    """
    with statsd.timer('orgs'):
        response = user.client.get(
            api_path('orgs'),
            params={'shared_with': user.username},
            auth=user.auth,
            name='/orgs?shared_with=[username]')
        statsd.incr('orgs_%s' % response.status_code)
    statsd.incr('orgs_no_requests')
    statsd.incr('no_requests')


def projects(user):
    """
    Projects endpoint.
    """
    with statsd.timer('projects'):
        response = user.client.get(
            api_path('projects'), auth=user.auth, name='/projects')
        statsd.incr('projects_%s' % response.status_code)
    statsd.incr('projects_no_requests')
    statsd.incr('no_requests')


def publish_form(user):
    """
    Publish an XLS Form
    """
    id_string = 'a' + uuid.uuid4().hex[:8]
    text_xls_form = [
        "survey\r\n"
        ",type,name,label\r\n"
        ",text,fruit,Fruit\r\n"
        "settings\r\n"
        "form_title,form_id\r\n"
        ",Demo %s,%s\r\n" % (id_string, id_string)
    ]
    data = {'text_xls_form': text_xls_form}
    with statsd.timer('forms'):
        response = user.client.post(
            api_path('forms'),
            auth=user.auth,
            data=data,
            name='/forms[publish]')
        statsd.incr('forms_%s' % response.status_code)
        if response.status_code == 201:
            user.id_string = response.json().get('id_string')
        else:
            logger.info(response.content)

    statsd.incr('forms_no_requests')
    statsd.incr('no_requests')


def post_submission(user):
    """
    Makes submission to /[username]/submission endpoint.
    """
    if not hasattr(user, 'id_string'):
        publish_form(user)
    instance_id = '%s' % uuid.uuid4()
    data = ('<?xml version="1.0" encoding="UTF-8" ?>'
            '<%(id_string)s id="%(id_string)s">'
            '<fruit>mango</fruit>'
            '<meta><instanceID>%(instance_id)s</instanceID></meta>'
            '</%(id_string)s>') % {
                'id_string': user.id_string,
                'instance_id': instance_id
            }
    files = {'xml_submission_file': ('submission.xml', data)}
    with statsd.timer('submission'):
        response = user.client.post(
            '/' + user.username + '/submission',
            auth=user.digest_auth,
            files=files,
            name='/submission')
        statsd.incr('submission_%s' % response.status_code)
    statsd.incr('submission_no_requests')
    statsd.incr('no_requests')
