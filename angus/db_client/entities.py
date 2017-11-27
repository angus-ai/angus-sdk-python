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
import collections

import requests.exceptions
from . import exceptions

GLOBAL = "global"
BY_DAY = "by_day"
BY_HOUR = "by_hour"

DATA_URL = os.getenv("DATA_URL", "https://data.angus.ai")

class MetricsGetter(object):
    def __init__(self, conf):
        """
        """
        self.conf = conf


class EntitiesGetter(MetricsGetter):
    def __init__(self, conf):
        """
        """
        super(EntitiesGetter, self).__init__(conf=conf)
        self.url = "{}/api/1/entities".format(DATA_URL)

    def get_entities(self, metrics, from_date, to_date=None, time=GLOBAL, page=None):
        """

        :param metrics:
        :param from_date:
        :param to_date:
        :param time:
        :param page:
        :return:
        """
        params = {
            "metrics": ",".join(metrics),
            "from_date": from_date.isoformat(),
        }

        if to_date:
            params.update({"to_date": to_date.isoformat()})
        if time:
            params.update({"time": time})
        if page:
            params.update({"page": page})

        res = self.conf.get(self.url, params=params)

        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                error = res.json()
                error_code = error["code"]
                if error_code in exceptions.EXCEPTIONS_CODE:
                    raise exceptions.EXCEPTIONS_CODE[error_code]("{}: {}".format(e.message, error['message']))
                else:
                    raise exceptions.HTTPError("{}: {}".format(e.message, error['message']))
            except ValueError:
                raise e

        json_res = res.json()
        return collections.OrderedDict(sorted(json_res.items()))

    def get_entities_by_hour(self, metrics, from_date, to_date=None, page=None):
        """

        :param metrics:
        :param from_date:
        :param to_date:
        :param page:
        :return:
        """
        return self.get_entities(metrics=metrics, from_date=from_date, to_date=to_date, time=BY_HOUR, page=page)

    def get_entities_by_day(self, metrics, from_date, to_date=None, page=None):
        """

        :param metrics:
        :param from_date:
        :param to_date:
        :param page:
        :return:
        """
        return self.get_entities(metrics=metrics, from_date=from_date, to_date=to_date, time=BY_DAY, page=page)

    def get_entities_globally(self, metrics, from_date, to_date=None, page=None):
        """

        :param metrics:
        :param from_date:
        :param to_date:
        :param page:
        :return:
        """
        return self.get_entities(metrics=metrics, from_date=from_date, to_date=to_date, time=GLOBAL, page=page)

    def get_entities_gen(self, metrics, from_date, to_date=None, time=GLOBAL, page=None):
        """

        :param metrics:
        :param from_date:
        :param to_date:
        :param time:
        :param page:
        :return:
        """
        json_res = self.get_entities(metrics, from_date, to_date, time, page)
        total_pages = json_res['nb_of_pages']
        current_page = json_res['page']

        while True:
            yield json_res['entities']
            if current_page < total_pages:
                json_res = self.get_entities(metrics, from_date, to_date, time, current_page+1)
                current_page = json_res['page']
            else:
                break
