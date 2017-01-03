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
import uuid
import re

from six.moves.urllib import parse as urlparse
import requests
import requests_futures.sessions
import logging
from Queue import Queue

__updated__ = "2017-01-03"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015-2017, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

logger = logging.getLogger('AngusSDK')

class Configuration(requests_futures.sessions.FuturesSession):

    def __init__(self):
        super(Configuration, self).__init__(max_workers=10)
        self.auth = None
        self.default_root = None
        self.timeout = None

    def set_credential(self, client_id, access_token):
        self.auth = requests.auth.HTTPBasicAuth(client_id, access_token)

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
        r = r.result()
        r.raise_for_status()
        self.representation = r.json()


def generate_encoder(attachments):
    class Encoder(json.JSONEncoder):

        def default(self, o):
            if isinstance(o, Resource):
                return o.endpoint
            if hasattr(o, 'read'):
                file_name = str(uuid.uuid1())
                field_name = "attachment://%s" % (file_name)
                attachments.append(
                    (field_name, (file_name, o, "application/octet-stream")))
                return field_name
            return json.JSONEncoder.default(self, o)

    return Encoder

BREAK = "\r\n"
DBREAK = BREAK+BREAK

def parse(data):
    """
    Parse multipart data stream to extract parts.
    """
    start = data.find("--myboundary\r\n")
    end = data.find(DBREAK, start)
    part = None
    if start != -1 and end != -1:
        end = end + len(DBREAK)
        header = data[start:end]
        content_length = re.search(r'Content-Length: (\w+)\r\n', header).group(1)
        content_length = int(content_length)
        if len(data) > (end+content_length):
            part = data[end:end+content_length]
            data = data[end+len(BREAK)+content_length:]
    return data, part


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

        r = r.result()
        r.raise_for_status()
        result = r.json()
        return resource_type(
            self.endpoint, result['url'], representation=result, conf=self.conf)


    def create_async(self, parameters, callback, resource_type=Resource):

        def store(res, resource_type, callback):
            res = res.result()
            res.raise_for_status()

            result = res.json()
            callback(resource_type(self.endpoint, result['url'],
                             representation=result, conf=self.conf))

        attachments = []

        data = json.dumps(parameters, cls=generate_encoder(attachments))

        if self.conf.executor._work_queue.qsize() > self.conf.executor._max_workers:
            logger.warn("There are too many requests awaiting to "
            "be sent. This request will be added to the queue but please try to decrease "
            "the rate at which \"process\" is called.")


        if attachments:
            files = attachments + [('meta', (None, data, 'application/json'))]
            r = self.conf.post(self.endpoint, files=files)
        else:
            headers = {'content-type': 'application/json'}
            r = self.conf.post(self.endpoint, data=data, headers=headers)

        r.add_done_callback(lambda fut: store(fut, resource_type, callback))
        return None

    def list(self, filters):
        r = self.conf.get(self.endpoint, params=filters)

        r = r.result()
        r.raise_for_status()

        result = r.json()
        return result


class Session():
    """State of the service store in the client
    """

    def __init__(self, service):
        self.service = service
        self.id = str(uuid.uuid1())

    def state(self):
        # TODO: for a short term, the server code will be statefull, and
        # use a session_id but it is bad, in a near future, client session will store
        # all information need by the service to compute the new result
        return {'session_id': self.id}


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
        self.streams = Collection(self.endpoint, 'streams',
                                  conf=self.conf)
        self.default_session = None
        self.session_parameters = None

    def process(
            self, parameters=None, async=False, session=None, callback=None):
        if parameters is None:
            parameters = {}
        else:
            parameters = copy.copy(parameters)

        if self.session_parameters is not None:
            parameters.update(self.session_parameters)

        if session is None:
            session = self.default_session

        if session is not None:
            parameters['state'] = session.state()

        parameters['async'] = async

        if callback:
            job = self.jobs.create_async(
                parameters,
                callback,
                resource_type=Job)
        else:
            job = self.jobs.create(
                parameters,
                resource_type=Job)
            return job


    def stream(
            self, parameters=None, data=None, session=None):

        if parameters is None:
            parameters = {}
        else:
            parameters = copy.copy(parameters)

        if self.session_parameters is not None:
            parameters.update(self.session_parameters)

        if session is None:
            session = self.default_session

        if session is not None:
            parameters['state'] = session.state()

        stream = self.streams.create(
            parameters,
            resource_type=Job)

        input_url = stream.result["input"]
        output_url = stream.result["output"]

        def parts():
            for params, field, part in data:
                buff = "\r\n".join(("--myboundary",
                                    "Content-Type: image/jpeg",
                                    "Content-Length: " + str(len(part)),
                                    "X-Angus-DataField: " + field,
                                    "X-Angus-Parameters: " + json.dumps(params),
                                    "",
                                    part,
                                    ""))
                yield buff
            yield "--myboundary--"


        self.conf.post(input_url, data=parts(), stream=True,
                               headers = {
                                   "Content-Type": "multipart/x-mixed-replace; boundary=myboundary",
                               })

        r = requests.get(output_url, stream=True, auth=self.conf.auth, verify=self.conf.verify)
        data = ""
        for content in r.iter_content(chunk_size=10): # read data as arrived
            data = data + content
            data, part = parse(data)
            if part is not None:
                yield part

    def get_description(self):
        return self.description.fetch()

    def create_session(self):
        session = Session(self)
        return session

    def enable_session(self, parameters=None):
        if self.default_session is None:
            self.default_session = self.create_session()

        if parameters is None:
            parameters = {}
        else:
            parameters = copy.copy(parameters)

        self.session_parameters = parameters

    def disable_session(self):
        self.default_session = None


class GenericService(Collection):

    """A no-versioned service, contains a collection of versioned services.
    """

    def __init__(self, *args, **kargs):
        super(GenericService, self).__init__(*args, **kargs)

    def get_service(self, version=None, service_class=Service):
        description = self.list({'version': version})
        description = description['versions']

        if version is None:
            description = max(description.items())[1]
        else:
            description = description[str(version)]

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
