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
import os
import sys
import urllib2

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


class Backend(object):

    def __init__(self, listen, start_script, stop_script):
        self.listen = listen
        self.listen_all = "0.0.0.0:%s" % listen.split(":", 1)[1]
        self.start_script = start_script
        self.stop_script = stop_script

    def msg(self, msg):
        print msg
        sys.stdout.flush()

    def is_listening(self):
        for conn in iter_connections():
            local, remote, state = conn
            if state != "LISTEN":
                continue
            if remote != "0.0.0.0:0":
                continue
            if local == self.listen or local == self.listen_all:
                return True
        return False

    def get_active_connections(self):
        for conn in iter_connections():
            local, remote, state = conn

            if local != self.listen and local != self.listen_all:
                continue

            if not state in ("ESTABLISHED", ):
                continue

            yield conn

    def wait_until_listening(self):
        self.msg("Waiting for '%s' to start listening" % self.listen)
        j = 1
        while True:
            for i in range(60):
                if self.is_listening():
                    return
                time.sleep(1)
            self.msg("  still hasn't started after %d minute(s)" % j)
            j = j + 1

    def wait_until_idle(self):
        self.msg("Waiting for '%s' to be idle" % self.listen)
        for i in range(60):
            connections = list(self.get_active_connections())
            if len(connections) == 0:
                self.msg("  now idle")
                return
            self.msg("  %d connections still active" % len(connections))
            time.sleep(1)

    def wake(self):
        if not self.wakeup:
            self.msg("Waiting grace period for warmup (%d seconds)" % self.grace)
            return

        self.msg("Hitting URL's to wake up backend")

        for url_part in self.wakeup:
            url = "http://%s/%s" % (self.listen, url_part.lstrip("/"))
            try:
                self.msg("  %s" % url)
                fp = urllib2.urlopen(url)
                fp.read()
            except:
                pass

    def start(self):
        self.msg(self.start_script)
        os.system(self.start_script)

    def stop(self):
        self.msg(self.stop_script)
        os.system(self.stop_script)

    def cycle(self):
        self.disable()
        self.wait_until_idle()
        self.stop()
        self.start()
        self.wait_until_listening()
        self.wake()
        self.enable()

