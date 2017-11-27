# -*- coding: utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import os
import requests
import requests.exceptions

from . import conf as db_conf
from . import exceptions

from .entities import EntitiesGetter


TOKEN_URL = os.getenv("CONSOLE_URL", "https://console.angus.ai")


def get_oauth_token(email, client_id, access_token, verify=True):
    """
    Get the JWT token for the provided credentials from the Angus console

    :param client_id: The client id of the stream
    :param access_token: The access token associated with this particular client id
    :return: the JWT token
    """
    data = {
        "username": email,
        "client_id": client_id,
        "access_token": access_token,
    }

    url = "{}/api-token-authstream/".format(TOKEN_URL)

    resp = requests.post(url, json=data, verify=verify)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        try:
            error = resp.json()
            raise exceptions.HTTPError("{}: {}".format(e.message, error['non_field_errors'][0]))
        except ValueError:
            raise e
    result = resp.json()

    if "token" in result:
        return result["token"]
    else:
        return None


class AuthenticationError(Exception):
    pass


def connect(email, url=None, conf=None, client_id=None,
            access_token=None, verify=True):
    """

    :param email:
    :param url:
    :param conf:
    :param client_id:
    :param access_token:
    :param verify:
    :return:
    """
    if None not in [email, client_id, access_token]:
        conf = db_conf.Configuration()
        try:
            jwt_token = get_oauth_token(email=email, client_id=client_id, access_token=access_token, verify=verify)
            conf.set_credential(jwt_token)
        except requests.exceptions.RequestException as e:
            print e
        if not verify:
            conf.do_not_verify()
    else:
        conf = db_conf.get_default_configuration(email)
    return EntitiesGetter(conf=conf)
