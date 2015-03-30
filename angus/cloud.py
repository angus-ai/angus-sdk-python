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

import angus

import rest

__updated__ = "2015-03-30"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"


class BlobDirectory(rest.Collection):

    def create(self, binary):
        return super(BlobDirectory, self).create(
            parameters={'content': binary})


class ServiceDirectory(rest.Collection):

    def get_service(self, name, version, service_class=rest.Service):
        description = self.list({'name': name})
        description = description['services']
        description = description[name]

        generic_service = rest.GenericService(
            self.endpoint,
            description['url'],
            conf=self.conf)
        service = generic_service.get_service(version, service_class)
        return service


class Root(rest.Resource):

    def __init__(self, url=None, conf=None):
        if conf is None:
            conf = angus.get_default_configuration()

        if url is None:
            url = conf.default_root

        super(Root, self).__init__(None, url, conf=conf)
        self.blobs = BlobDirectory(self.endpoint, 'blobs', conf=self.conf)
        self.services = ServiceDirectory(self.endpoint, 'services',
                                         conf=self.conf)
