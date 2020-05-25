# -*- coding=utf-8 -*-
"""
Simulates Zebra user behaviour
"""
import logging
import random

from locust import HttpLocust, TaskSet
from requests.auth import HTTPDigestAuth
from statsd import StatsClient, TCPStatsClient

from onadata_libs import (orgs_shared_with, post_submission, projects,
                          publish_form, user_profile)
from users import USERS

logger = logging.getLogger(__name__)  # pylint: disable=C0103


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
            self.digest_auth = HTTPDigestAuth(*random_user)
            login(self)


class ZebraUser(HttpLocust):
    """
    Defines the normal behaviour of a Zebra user.
    """
    task_set = UserBehaviour
    min_wait = 5000
    max_wait = 9000
