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
import six

from angus.client import rest
import angus

__updated__ = "2017-08-07"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015-2017, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

class BlobDirectory(rest.Collection):
    """ Store binary data.
    """
    def create(self, binary):
        return super(BlobDirectory, self).create(
            parameters={'content': binary})


def generate_encoder(root):
    """ Replace binary data in python data structure by uploading
    it as a blob in Angus.ai cloud and set an endpoint.
    """
    class Encoder(json.JSONEncoder):

        def default(self, o):
            if isinstance(o, rest.Resource):
                return o.endpoint
            if hasattr(o, 'read'):
                res = root.blobs.create(o)
                return res.endpoint
            return json.JSONEncoder.default(self, o)
    return Encoder


class CompositeService(rest.Resource):
    """ Call several services as if it were only one.
    """

    def __init__(self, *args, **kwargs):
        self.services = kwargs.pop("services")
        super(CompositeService, self).__init__(*args, **kwargs)
        self.root = Root(conf=self.conf)
        self.default_session = None
        self.session_parameters = None

    def process(self, parameters, async=False, session=None, callback=None):
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

        attachments = []

        data = json.dumps(parameters, cls=generate_encoder(self.root))

        futures = []
        for name, service in six.iteritems(self.services):
            if attachments:
                files = attachments + \
                    [('meta', (None, data, 'application/json'))]
                resp = self.conf.post(service.jobs.endpoint, files=files)
            else:
                headers = {'content-type': 'application/json'}
                resp = self.conf.post(
                    service.jobs.endpoint,
                    data=data,
                    headers=headers)
            futures.append((name, resp))

        result = {}
        for (name, resp) in futures:
            resp = resp.result()
            if resp.status_code < 400:
                result[name] = resp.json()

        result["status"] = 200

        job = rest.Job(
            self.endpoint, "", representation=result, conf=self.conf)

        if job.status == rest.Resource.CREATED and callback:
            callback(job)

        return job

    def create_session(self):
        """Create a new session
        """
        session = rest.Session(self)
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


class ServiceDirectory(rest.Collection):
    """The collection of services.
    """

    def get_service(self, name, version=None, service_class=rest.Service):
        """Get an unique service by name and version.

        Arguments:
        name -- name of the service
        version -- the version of the service
        """
        description = self.list({'name': name})
        description = description['services']
        if name in description:
            description = description[name]
        else:
            raise Exception("No such service")

        generic_service = rest.GenericService(
            self.endpoint,
            description['url'],
            conf=self.conf)
        service = generic_service.get_service(version, service_class)
        return service

    def get_services(self, services=None):
        """Get a generic services by name.

        Arguments:
        services -- list of name or list of tuple (name, version)
        """
        description = self.list({})
        description = description['services']
        if services is None:
            services = description

        cservices = dict()
        for name in services:
            if isinstance(name, tuple):
                version = name[1]
                name = name[0]
            else:
                version = None

            service = self.get_service(name, version)
            cservices[name] = service

        return CompositeService(
            "memory:///", "composite", services=cservices, conf=self.conf)


class Root(rest.Resource):
    """The root resource of the Angus.ai cloud.
    With blobs and services collections.
    """

    def __init__(self, url=None, conf=None):
        if conf is None:
            conf = angus.client.get_default_configuration()

        if url is None:
            url = conf.default_root
        else:
            conf.default_root = url

        if url is None:
            raise Exception("Root url must be provided, please run angusme, "
                            "or define the url as argument.")

        super(Root, self).__init__(None, url, conf=conf)
        self.blobs = BlobDirectory(self.endpoint, 'blobs', conf=self.conf)
        self.services = ServiceDirectory(self.endpoint, 'services',
                                         conf=self.conf)
