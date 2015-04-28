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


import copy
import json
import urlparse
import uuid

import requests


__updated__ = "2015-04-28"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"


class Configuration(requests.Session):

    def __init__(self):
        super(Configuration, self).__init__()
        self.auth = None
        self.default_root = None

    def set_credential(self, client_id, access_token):
        self.auth = requests.auth.HTTPBasicAuth(client_id, access_token)

    def set_ca_path(self, ca_path):
        self.verify = ca_path

    def do_not_verify(self):
        self.verify = False


class Resource(object):

    CREATED = 201
    ACCEPTED = 202

    def __init__(self, parent, name, representation=None, conf=None):
        self.parent = parent
        self.name = name
        self.endpoint = urlparse.urljoin("%s/" % (self.parent), name)
        self.representation = representation
        self.conf = conf

    @property
    def status(self):
        if self.representation is not None:
            return self.representation['status']
        else:
            return None

    def fetch(self):
        r = self.conf.get(self.endpoint)
        r.raise_for_status()
        self.representation = r.json()


def generate_encoder(attachments):
    class Encoder(json.JSONEncoder):

        def default(self, o):
            if isinstance(o, Resource):
                return o.endpoint
            if hasattr(o, 'read'):
                file_name = unicode(uuid.uuid1())
                field_name = "attachment://%s" % (file_name)
                attachments.append(
                    (field_name, (file_name, o, "application/octet-stream")))
                return field_name
            return json.JSONEncoder.default(self, o)

    return Encoder


class Collection(Resource):

    def __init__(self, *args, **kargs):
        super(Collection, self).__init__(*args, **kargs)

    def create(self, parameters, resource_type=Resource):

        attachments = []

        data = json.dumps(parameters, cls=generate_encoder(attachments))

        if attachments:
            files = attachments + [('meta', (None, data, 'application/json'))]
            r = self.conf.post(self.endpoint, files=files)
        else:
            headers = {'content-type': 'application/json'}
            r = self.conf.post(self.endpoint, data=data, headers=headers)

        r.raise_for_status()

        result = r.json()
        return resource_type(
            self.endpoint, result['url'], representation=result, conf=self.conf)

    def list(self, filters):
        r = self.conf.get(self.endpoint, params=filters)

        r.raise_for_status()

        result = r.json()
        return result


class Service(Resource):

    """A service is a resource on which we can create a new job, i.e. record
    a new task in the cloud.
    """

    def __init__(self, *args, **kargs):
        super(Service, self).__init__(*args, **kargs)

        self.description = Resource(self.endpoint, 'description',
                                    conf=self.conf)
        self.jobs = Collection(self.endpoint, 'jobs',
                               conf=self.conf)

    def process(
            self, parameters=None, async=False, callback=None):
        if parameters is None:
            parameters = {}
        else:
            parameters = copy.copy(parameters)

        parameters['async'] = async

        job = self.jobs.create(
            parameters,
            resource_type=Job)

        if job.status == Resource.CREATED and callback:
            callback(job)

        return job

    def get_description(self):
        return self.description.fetch()


class GenericService(Collection):

    """A no-versioned service, contains a collection of versioned services.
    """

    def __init__(self, *args, **kargs):
        super(GenericService, self).__init__(*args, **kargs)

    def get_service(self, version, service_class=Service):
        description = self.list({'version': version})
        description = description['versions']
        description = description[unicode(version)]
        return service_class(self.endpoint, description['url'],
                             conf=self.conf)


class Job(Resource):

    """A job is a compute task in the cloud
    """

    def __init__(self, *args, **kargs):
        super(Job, self).__init__(*args, **kargs)

    @property
    def result(self):
        return self.representation
