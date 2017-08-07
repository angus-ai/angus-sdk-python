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
import logging

from six.moves.urllib import parse as urlparse
import requests
import requests_futures.sessions


__updated__ = "2017-08-07"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015-2017, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

LOGGER = logging.getLogger('AngusSDK')

MULTIPART_HEADER = {
    "Content-Type": "multipart/x-mixed-replace; boundary=myboundary"
}

class Configuration(requests_futures.sessions.FuturesSession):
    """A configuration of connection with Angus.ai cloud.
    """
    def __init__(self):
        super(Configuration, self).__init__(max_workers=10)
        self.auth = None
        self.default_root = None
        self.timeout = None
        self.verify = True

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
    """A resource is the root object of the Angus.ai API,
    an endpoint with a representation (json).
    This class can sync with the remote resource, and check the status
    """

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
        """Return the current resource status.
        """
        if self.representation is not None:
            return self.representation['status']
        else:
            return None

    def fetch(self):
        """Synchronize with the online resource.
        """
        res = self.conf.get(self.endpoint)
        res = res.result()
        res.raise_for_status()
        self.representation = res.json()


def generate_encoder(attachments):
    """Generate a JSON encoder that replaces binary data with
    reference to an part of multipart request.
    """
    class Encoder(json.JSONEncoder):
        """The encoder
        """
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
    """Parse multipart data stream to extract parts.
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

def generate_parts(data):
    """Generate parts for a multipart stream from the generator data.
    """
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

class Collection(Resource):
    """A collection is a set of Ressources, this class
    enable creation of sub resource (childs) and list them.
    """
    def __init__(self, *args, **kargs):
        super(Collection, self).__init__(*args, **kargs)

    def __store(self, res, resource_type, callback):
        res = res.result()
        res.raise_for_status()

        result = res.json()
        callback(resource_type(self.endpoint, result['url'],
                               representation=result, conf=self.conf))

    def create(self, parameters, resource_type=Resource):
        """Create a new child resource.

        Arguments:
        parameters -- the resource creation parameters (default {})
        resource_type -- The class of the new resource (default Resource)
        """
        attachments = []

        data = json.dumps(parameters, cls=generate_encoder(attachments))

        if attachments:
            files = attachments + [('meta', (None, data, 'application/json'))]
            resp = self.conf.post(self.endpoint, files=files)
        else:
            headers = {'content-type': 'application/json'}
            resp = self.conf.post(self.endpoint, data=data, headers=headers)

        result = resp.result()
        result.raise_for_status()
        result = result.json()
        return resource_type(
            self.endpoint, result['url'], representation=result, conf=self.conf)

    def create_async(self, parameters, callback, resource_type=Resource):
        """Create a new child resource asynchronously.

        Arguments:
        parameters -- the resource creation parameters (default {})
        callback -- a callback when resource is created
        resource_type -- The class of the new resource (default Resource)
        """
        attachments = []

        data = json.dumps(parameters, cls=generate_encoder(attachments))

        if self.conf.executor._work_queue.qsize() > self.conf.executor._max_workers:
            LOGGER.warn("There are too many requests awaiting to "
            "be sent. This request will be added to the queue but please try to decrease "
            "the rate at which \"process\" is called.")


        if attachments:
            files = attachments + [('meta', (None, data, 'application/json'))]
            resp = self.conf.post(self.endpoint, files=files)
        else:
            headers = {'content-type': 'application/json'}
            resp = self.conf.post(self.endpoint, data=data, headers=headers)

        resp.add_done_callback(lambda fut: self.__store(fut, resource_type, callback))
        return None

    def list(self, filters):
        """List sub-resources.
        """
        resp = self.conf.get(self.endpoint, params=filters)

        resp = resp.result()
        resp.raise_for_status()

        result = resp.json()
        return result

class Session(object):
    """State of the service store in the client
    """

    def __init__(self, service):
        self.service = service
        self.id = str(uuid.uuid1())

    def state(self):
        """The session state.
        """
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

    def process(self, parameters=None, async=False, session=None, callback=None):
        """Create a job configurate with

        Arguments:
        parameters -- the job parameter (default {})
        async -- request an async job (default False)
        session -- a session object (default None)
        callback -- for async jobs, a callback when result is available (default None)
        """
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

    def stream(self, parameters=None, data=None, session=None):
        """Create a stream object with input and output.
        Consume data generator and also return a generator for results.

        Arguments:
        parameters -- parameter for stream creation (default {})
        data -- generator that produces (data_parameters, data_field, data_bin)
        data_parameters -- parameters for this data "frame"
        data_field -- the field in parameters set with the binary data
        data_bin -- the binary data
        session -- a session object (default None)
        """

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

        self.conf.post(input_url, data=generate_parts(data), stream=True,
                       headers=MULTIPART_HEADER)

        resp = requests.get(output_url, stream=True, auth=self.conf.auth, verify=self.conf.verify)
        data = ""
        for content in resp.iter_content(chunk_size=10): # read data as arrived
            data = data + content
            data, part = parse(data)
            if part is not None:
                yield part

    def get_description(self):
        """Return the description of the service
        """
        return self.description.fetch()

    def create_session(self):
        """Create a new session
        """
        session = Session(self)
        return session

    def enable_session(self, parameters=None):
        """Create a new session and set it as default in this service.
        """
        if self.default_session is None:
            self.default_session = self.create_session()

        if parameters is None:
            parameters = {}
        else:
            parameters = copy.copy(parameters)

        self.session_parameters = parameters

    def disable_session(self):
        """Remove default session for this service.
        """
        self.default_session = None


class GenericService(Collection):

    """A no-versioned service, contains a collection of versioned services.
    """

    def __init__(self, *args, **kargs):
        super(GenericService, self).__init__(*args, **kargs)

    def get_service(self, version=None, service_class=Service):
        """Get a versioned service.
        """
        description = self.list({'version': version})
        description = description['versions']

        if version is None:
            description = max(description.items())[1]
        else:
            description = description[str(version)]

        return service_class(self.endpoint, description['url'],
                             conf=self.conf)

class Job(Resource):

    """A job is a compute task in the cloud.
    """

    def __init__(self, *args, **kargs):
        super(Job, self).__init__(*args, **kargs)

    @property
    def result(self):
        """Get the result of the job, i.e. the representation
        of the job resource.
        """
        return self.representation
