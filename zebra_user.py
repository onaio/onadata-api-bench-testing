# -*- coding=utf-8 -*-
"""
Ona API locust file.
"""
import logging
import random

from requests.auth import AuthBase, HTTPDigestAuth

from locust import HttpLocust, TaskSet
from users import USERS

logger = logging.getLogger(__name__)  # pylint: disable=C0103


# pylint: disable=R0903
class TempTokenAuth(AuthBase):
    """
    TempToken Authorization class.

    Adds "Authorization" header with "TempToken [token]" to a request.
    """

    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers['Authorization'] = 'TempToken: %s' % self.token

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
    user.client.get(
        api_path('profiles/' + user.username),
        auth=user.auth,
        name='/profiles/[username]')


def orgs_shared_with(user):
    """
    Orgs endpoint for orgs shared with the user.
    """
    user.client.get(
        api_path('orgs'),
        params={'shared_with': user.username},
        auth=user.auth)


class UserBehaviour(TaskSet):
    """
    API user behaviour.
    """
    auth = None
    tasks = {user_profile: 1, orgs_shared_with: 1}

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
