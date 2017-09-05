# -*- coding=utf-8 -*-
"""
List of user usernames and passwords
"""

import codecs
import csv
import os


def load_users():
    """
    Returns a list of usernames and password file from 'users.csv' file when
    present.
    """
    users = []
    filename = 'users.csv'
    if os.path.exists(filename):
        with codecs.open(filename, 'rb', encoding='utf-8') as users_file:
            reader = csv.reader(users_file)
            for row in reader:
                users.append(tuple(row[:2]))
    return users


USERS = load_users()

if __name__ == '__main__':
    print(load_users())
