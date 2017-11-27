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
import json


import angus.db_client
from requests import Session

class Configuration(Session):
    """A configuration of connection with Angus.ai cloud.
    """
    def __init__(self):
        super(Configuration, self).__init__()
        self.default_root = None
        self.timeout = None
        self.verify = True

    def set_credential(self, jwt_token):
        self.headers = {"Authorization": "Bearer {}".format(jwt_token)}

    def set_ca_path(self, ca_path):
        self.verify = ca_path

    def do_not_verify(self):
        self.verify = False

    def get(self, *args, **kwargs):
        if self.timeout:
            kwargs.setdefault("timeout", self.timeout)
        return super(Configuration, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.timeout:
            kwargs.setdefault("timeout", self.timeout)
        return super(Configuration, self).post(*args, **kwargs)


def get_default_configuration(email):
    """Get and parse the default configuration in ~/.angusdk/config.json
    """
    # Get the configuration file
    default_file = os.path.realpath("./config.json")
    if os.path.isfile(default_file):
        conf_file = default_file
    else:
        default_file = os.path.expanduser("~/.angusdk/config.json")

        if os.path.isfile(default_file):
            conf_file = default_file
        else:
            conf_file = None

    conf = Configuration()

    # Apply the configuration file if it exists
    if conf_file is not None:
        with open(conf_file, 'r') as fconf:
            conf_data = json.loads(fconf.read())
            if 'client_id'in conf_data and 'access_token' in conf_data:
                jwt_token = angus.db_client.get_oauth_token(
                    email,
                    conf_data['client_id'],
                    conf_data['access_token']
                )
                if jwt_token:
                    conf.set_credential(jwt_token)

            if 'ca_path' in conf_data:
                conf.set_ca_path(conf_data['ca_path'])

            if 'default_root' in conf_data:
                conf.default_root = conf_data['default_root']

    return conf
