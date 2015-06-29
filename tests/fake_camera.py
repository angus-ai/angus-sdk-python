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

from os import listdir
from os.path import isfile, join


class Camera(object):

    def __init__(self, path):
        self.files = [join(path, f) for f in listdir(path)]
        self.files = sorted([f for f in self.files if isfile(f)])
        self.current = 0

    def reset(self):
        self.current = 0

    def has_next(self):
        return self.current < len(self.files)

    def next(self):
        img = open(self.files[self.current], 'rb').read()
        self.current += 1
        return img
