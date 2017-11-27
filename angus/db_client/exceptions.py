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

"""
angus.db_client.exceptions
~~~~~~~~~~~~~~~~~~~

This module contains the set of the db API's exceptions.
"""



class AngusApiException(IOError):
    """There was an ambiguous exception that occurred while handling your
    request.
    """

    def __init__(self, *args, **kwargs):
        """Initialize AngusApiException with `request` and `response` objects."""
        response = kwargs.pop('response', None)
        self.response = response
        self.request = kwargs.pop('request', None)
        if (response is not None and not self.request and
                hasattr(response, 'request')):
            self.request = self.response.request
        super(AngusApiException, self).__init__(*args, **kwargs)


class HTTPError(AngusApiException):
    """An HTTP error occurred."""


class UnauthorizedError(AngusApiException):
    """Something is wrong with the users's authentication."""


class UnexistingTimeError(AngusApiException):
    """Something is wrong with the users's authentication."""


class UnexistingMetricError(AngusApiException):
    """The user asked for an unexisting Metric."""


class PageNotExistingError(AngusApiException):
    """The user asked for an unexisting Metric."""


class MissingParamError(AngusApiException):
    """The user didn't provide a mandatory parameter with the request."""

EXCEPTIONS_CODE = {
    "authorization_header_missing": UnauthorizedError,
    "unexisting_time": UnexistingTimeError,
    "unexisting_metric": UnexistingMetricError,
    "page_not_existing": PageNotExistingError,
    "missing_mandatory_param": MissingParamError,
}
