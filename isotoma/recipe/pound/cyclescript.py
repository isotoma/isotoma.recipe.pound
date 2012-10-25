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
import subprocess

from isotoma.recipe.pound.backend import Backend

class PoundBackend(Backend):

    def __init__(self, cfg, idx, listen, start_script, stop_script):
        self.grace = cfg.getint("cycle", "grace")
        self.control = cfg.get("cycle", "control")
        self.poundctl = cfg.get("cycle", "poundctl")
        self.wakeup = [x.strip() for x in cfg.get("cycle", "wakeup").strip().split("\n") if x.strip()] 
        self.idx = idx

        Backend.__init__(self, listen, start_script, stop_script)

    def enable(self):
        s = "%s -c %s -B 0 0 %d" % (self.poundctl, self.control, self.idx)
        self.msg(s)
        os.system(s)

    def disable(self):
        s = "%s -c %s -b 0 0 %d" % (self.poundctl, self.control, self.idx)
        self.msg(s)
        os.system(s)


def iter_backends(cfg):
    prefix = os.path.dirname(sys.argv[0])

    backends = cfg.get("cycle", "backends")
    backends = [x.strip().split(":") for x in backends.strip().split("\n")]

    for idx, backend in enumerate(backends):
        ip, port, stop_script, start_script = backends[idx]
        address = ":".join((ip, port))

        if not start_script.startswith("/"):
            start_script = os.path.join(prefix, start_script)

        if not stop_script.startswith("/"):
            stop_script = os.path.join(prefix, stop_script)

        yield PoundBackend(cfg,
            idx,
            address,
            start_script,
            stop_script,
            )


def execute(inifile):
    cfg = ConfigParser.ConfigParser()
    cfg.read(inifile)

    for b in iter_backends(cfg):
        b.cycle()

