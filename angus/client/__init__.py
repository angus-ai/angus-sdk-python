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

import argparse
import json
import logging
import os

import sys

import requests

import angus.client.cloud
import angus.client.rest
from . import version

__version__ = version.__version__
__updated__ = "2017-08-08"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015-2017, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

LOGGER = logging.getLogger('AngusCLIENT')
logging.basicConfig()

requests.packages.urllib3.disable_warnings()

def parse_cmd_line(argv):
    """Parse command line argument. See -h option.
    """
    formattter_class = argparse.RawDescriptionHelpFormatter

    parser = argparse.ArgumentParser(description='Angus CLIENT',
                                     formatter_class=formattter_class)

    parser.add_argument('-c', '--configuration', metavar='filename', type=str,
                        help='configuration file.')

    parser.add_argument('-id', '--clientid', metavar='clientid', type=str,
                        help='the client id.')

    parser.add_argument('-a', '--access', metavar='access', type=str,
                        help='the access token.')

    parser.add_argument('-v', '--verbose', dest='vlevel', action='count',
                        default=0,
                        help='increases log vervosity for each occurence.')

    parser.add_argument('-ca', '--capath', metavar='capath', type=str,
                        help='path to a trusted ca bundle.')

    parser.add_argument('-r', '--root', metavar='root', type=str,
                        help='the angus gate url')

    parser.add_argument('--version', action='version',
                        version="%(prog)s {}".format(__version__))

    args = parser.parse_args(argv)

    return args

def get_default_configuration(argv=""):
    """Get and parse the default configuration in ~/.angusdk/config.json
    """
    args = parse_cmd_line(argv)

    # Set the logger level
    logging.basicConfig()
    LOGGER.setLevel(max(3 - args.vlevel, 0) * 10)

    # Get the configuration file
    default_file = os.path.realpath("./config.json")
    if args.configuration is not None:
        if os.path.isfile(args.configuration):
            conf_file = args.configuration
        else:
            LOGGER.error("The configuration file '%s' does not exist",
                         args.configuration)
            sys.exit(-1)
    elif os.path.isfile(default_file):
        conf_file = default_file
    else:
        default_file = os.path.expanduser("~/.angusdk/config.json")

        if os.path.isfile(default_file):
            conf_file = default_file
        else:
            conf_file = None

    conf = angus.client.rest.Configuration()

    # Apply the configuration file if it exists
    if conf_file is not None:
        with open(conf_file, 'r') as fconf:
            conf_data = json.loads(fconf.read())
            if 'client_id'in conf_data and 'access_token' in conf_data:
                conf.set_credential(
                    conf_data['client_id'],
                    conf_data['access_token'])

            if 'ca_path' in conf_data:
                conf.set_ca_path(conf_data['ca_path'])

            if 'default_root' in conf_data:
                conf.default_root = conf_data['default_root']

    if args.clientid and args.access:
        conf.set_credential(args.clientid, args.access)

    if args.root:
        conf.default_root = args.root

    if args.capath:
        conf.set_ca_path(args.capath)

    return conf

def connect(url=None, conf=None, client_id=None,
            access_token=None, verify=True):
    """Create a resource root with the given configuration.
    """
    if None not in [client_id, access_token]:
        conf = angus.client.rest.Configuration()
        conf.set_credential(client_id, access_token)
        if not verify:
            conf.do_not_verify()

    return angus.client.cloud.Root(url, conf)
