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

import json
import datetime

import angus
import pytz

c = angus.connect(url="https://mgate.angus.ai",
              client_id="",
              access_token="",
              verify=False)

s = c.services.get_service("scene_analysis")
s.enable_session()

def data():
    """Frame generator
    """
    with open("macgyver.jpg", "rb") as image_file:
        img = image_file.read()

    for _ in range(20):
        timestamp = datetime.datetime.now(pytz.utc)

        yield ({"timestamp": timestamp.isoformat()}, "image", img)

for job in s.stream(data=data()):
    print(json.loads(job))
