# Copyright 2010 Isotoma Limited
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

import sys
import os
import time
import shutil
import ConfigParser
import xml.dom.minidom
import subprocess
from isotoma.recipe.pound.netstat import wait_for_backend


class WaitForBackend(object):
    def __init__(self, backend):
        self.backend = backend
    def __call__(self):
        print "waiting for connections to %s to terminate" % self.backend
        wait_for_backend(self.backend)


class WaitForTimeout(object):
    def __init__(self, grace):
        self.grace = grace
    def __call__(self):
        print "sleeping for", self.grace
        time.sleep(self.grace)


def get_waiters(control):
    p = subprocess.Popen(["poundctl", "-c", control, "-X"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    if stderr:
        return {}

    # Oh pound / XML, one or both of you suck...
    stdout = stdout.replace("HTTP address", "HTTP='1' address")

    dom = xml.dom.minidom.parseString(stdout)
    for listener in dom.getElementsByTagName("listener"):
        if listener.getAttribute("index") == "0":
            retval = {}
            for backend in listener.getElementsByTagName("backend"):
                retval[int(backend.getAttribute("index"))] = WaitForBackend(backend.getAttribute("address"))
            return retval

    return {}


def execute(inifile):
    cfg = ConfigParser.ConfigParser()
    cfg.read(inifile)
    grace = cfg.getint("cycle", "grace")
    control = cfg.get("cycle", "control")
    poundctl = cfg.get("cycle", "poundctl")
    backends = cfg.get("cycle", "backends")
    backends = [x.strip().split(":") for x in backends.strip().split("\n")]

    grace = WaitForTimeout(grace)
    waiters = get_waiters(control)

    # if the start/stop scripts do not start with / we assume they are alongside argv[0]
    prefix = os.path.dirname(sys.argv[0])
    for i, (stop, start) in enumerate(backends):
        if not start.startswith("/"):
            start = os.path.join(prefix, start)
        if not stop.startswith("/"):
            stop = os.path.join(prefix, stop)

        s = "%s -c %s -b 0 0 %d" % (poundctl, control, i)
        print s
        os.system(s)

        waiters.get(i, grace)()

        print stop
        os.system(stop)

        print start
        os.system(start)

        s = "poundctl -c %s -B 0 0 %d" % (control, i)
        print s
        os.system(s)

        grace()

