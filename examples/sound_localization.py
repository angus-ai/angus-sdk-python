#!/usr/bin/env python
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

try:
    import Queue
except ImportError:
    import queue as Queue

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import wave

import angus.client
import pyaudio

__updated__ = "2017-01-02"
__author__ = "Aurélien Moreau"
__copyright__ = "Copyright 2015-2017, Angus.ai"
__credits__ = ["Aurélien Moreau", "Gwennael Gate", "Raphaël Lumbroso"]
__license__ = "Apache v2.0"
__maintainer__ = "Aurélien Moreau"
__status__ = "Production"

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
RECORD_SECONDS = 2
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()
host_info = p.get_default_host_api_info()
INDEX = host_info['defaultInputDevice']

print(host_info)
print()
print()
print(p.get_device_info_by_host_api_device_index(0, INDEX))
print()
print()

conn = angus.client.connect()
service = conn.services.get_service('sound_localization', version=1)

stream_queue = Queue.Queue()


def callback(in_data, frame_count, time_info, status):
    stream_queue.put(in_data)
    # print(stream_queue.qsize())
    return (in_data, pyaudio.paContinue)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=INDEX,
                stream_callback=callback)


print("* recording")
stream.start_stream()
j = 0
while j < 30:
    frames = []
    j += 1

    for i in range(int(RATE / CHUNK / 2)):
        data = stream_queue.get()
        frames.append(data)

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    job = service.process(
        {
            'sound': open(WAVE_OUTPUT_FILENAME, 'rb'),
            'sensitivity': 1.0,
            'baseline': 1.0,
        }
    )

    print(job.result)


stream.stop_stream()
print("* done recording")

stream.close()
p.terminate()
