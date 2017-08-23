#! /usr/bin/env python
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

import angus.client
import time

__updated__ = "2017-08-23"
__author__ = "Gwennael Gate"
__copyright__ = "Copyright 2015-2017, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate", "Raphaël Lumbroso"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"


def async_res(fut):
    job = fut.result()
    # Print the result of the job.
    print(job.result['faces'])

def main():
    # Get the conn resource of Angus Cloud
    conn = angus.client.connect()

    # Get the service 'face_detection' in version 1
    service = conn.services.get_service('face_detection', version=1)

    # Submit a new job to the service, and get the result asynchronously
    job_future = service.process_async({'image': open('macgyver.jpg', 'rb')})

    # You can either work in the future callback to get the result
    job_future.add_done_callback(async_res)
    print("You can do something else here")

    # Or wait directly for the result in the main function :
    # res = job_future.result()
    # print(res.result['faces'])

if __name__ == '__main__':
    main()
