# Copyright 2012 Isotoma Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

CONNECTION_STATE = {
    '01':'ESTABLISHED',
    '02':'SYN_SENT',
    '03':'SYN_RECV',
    '04':'FIN_WAIT1',
    '05':'FIN_WAIT2',
    '06':'TIME_WAIT',
    '07':'CLOSE',
    '08':'CLOSE_WAIT',
    '09':'LAST_ACK',
    '0A':'LISTEN',
    '0B':'CLOSING'
    }

def convert_ip(data):
    dec = lambda hx: str(int(hx, 16))
    ip = lambda s: '.'.join((dec(s[6:8]),dec(s[4:6]),dec(s[2:4]),dec(s[0:2])))
    host, port = data.split(':')
    return ":".join((ip(host), dec(port)))

def iter_tcp_connection_lines():
    f = open("/proc/net/tcp", "r")
    f.readline()
    while True:
        line = f.readline()
        if not line:
            break
        yield line
    f.close()

def iter_connections():
    for line in iter_tcp_connection_lines():
        sl, rest = line.split(": ", 1)
        local, remote, state, rest = rest.split(" ", 3)

        local = convert_ip(local)
        remote = convert_ip(remote)
        state = CONNECTION_STATE.get(state, "UNKNOWN")

        yield local, remote, state


def iter_connections_for_backend(backend):
    #listening = False
    #h, p = backend.split(":")
    #anylisten = "0.0.0.0:%s" % p

    for conn in iter_connections():
        local, remote, state = conn

        #if local == anylisten and state == "LISTEN":
        #    listening = True
        #    continue

        if local != backend:
            continue

        #if state == "LISTEN":
        #    listening = True
        #    continue

        if not state in ("ESTABLISHED", ):
            continue

        yield conn

    #if not listening:
    #    raise ValueError("Service '%s' doesn't seem to be listening" % backend)


def wait_for_backend(backend):
    for i in range(60):
        connections = list(iter_connections_for_backend(backend))
        if len(connections) == 0:
            return
        print len(connections), "left"
        time.sleep(1)

