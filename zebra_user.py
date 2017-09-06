# -*- coding=utf-8 -*-
"""
Ona API locust file.
"""
import logging
import random
import uuid
import graphite
import os

from statsd import TCPStatsClient, StatsClient
from locust import HttpLocust, TaskSet
from requests.auth import AuthBase, HTTPDigestAuth
from locust import HttpLocust, TaskSet
from users import USERS

logger = logging.getLogger(__name__)  # pylint: disable=C0103
statsd = StatsClient(host=os.environ.get('STATSD_HOST', '127.0.0.1'),
                     port=os.environ.get('STATSD_PORT', 8125),
                     prefix=os.environ.get('STATSD_PREFIX', 'locust'))


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
    response = user.client.get(api_path('user'), auth=user.auth, name='/user')
    user.temp_token = response.json().get('temp_token')
    user.username = response.json().get('username')
    user.auth = TempTokenAuth(user.temp_token) \
        if hasattr(user, 'temp_token') else None


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
    user.client.get(
        api_path('orgs'),
        params={'shared_with': user.username},
        auth=user.auth,
        name='/orgs?shared_with=[username]')


def projects(user):
    """
    Projects endpoint.
    """
    user.client.get(api_path('projects'), auth=user.auth, name='/projects')


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
    response = user.client.post(
        api_path('forms'), auth=user.auth, data=data, name='/forms[publish]')
    if response.status_code == 201:
        user.id_string = response.json().get('id_string')


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
    user.client.post(
        '/' + user.username + '/submission', files=files, name='/submission')


class UserBehaviour(TaskSet):
    """
    API user behaviour.
    """
    auth = None
    tasks = {
        user_profile: 1,
        orgs_shared_with: 2,
        projects: 2,
        publish_form: 1,
        post_submission: 5
    }

    def on_start(self):
        """
        On start login to the api.
        """
        if not self.auth:
            random_user = random.choice(USERS)
            logger.info(
                "\n---------------------------------------------------------"
                "\n                 Authenticating %s. "
                "\n---------------------------------------------------------",
                random_user[0])
            self.auth = HTTPDigestAuth(*random_user)
            login(self)


class ZebraUser(HttpLocust):
    """
    Defines the normal behaviour of a Zebra user.
    """
    task_set = UserBehaviour
    min_wait = 5000
    max_wait = 9000
