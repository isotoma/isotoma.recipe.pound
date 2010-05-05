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

import logging
import sys
import os
import time
import zc.buildout
import shutil
import ConfigParser

class Cycle(object):

    def __init__(self, buildout, name, options):
        self.name = name
        self.buildout = buildout
        self.options = options
        self.options.setdefault("grace", "30")
        self.options.setdefault('control', os.path.join(self.buildout['buildout']['directory'], "var", "%s.ctl" % self.name))
        self.options.setdefault('poundctl', "/usr/sbin/poundctl")

    def install(self):
        outputdir = os.path.join(self.buildout['buildout']['directory'], self.name)
        if not os.path.exists(outputdir):
            os.mkdir(outputdir)
        ininame = os.path.join(outputdir, "cycle.ini")
        ini = open(ininame, "w")
        print >>ini, "[cycle]"
        print >>ini, "grace = %s" % (self.options['grace'],)
        print >>ini, "control = %s" % (self.options['control'],)
        print >>ini, "poundctl = %s" % (self.options['poundctl'],)
        print >>ini, "backends = %s" % "\n    ".join(self.options['backends'].split("\n"))
        target=os.path.join(self.buildout["buildout"]["bin-directory"],self.name)
        script = open(target, "w")
        print >>script, "#! /usr/bin/env %s" % self.buildout['buildout']['executable']
        print >>script, "from isotoma.recipe.pound import cycle"
        print >>script, "cycle.execute('%s')" % (ininame,)
        os.chmod(target, 0755)
        return [outputdir]

    def update(self):
        pass    

def execute(inifile):
    cfg = ConfigParser.ConfigParser()
    cfg.read(inifile)
    grace = cfg.getint("cycle", "grace")
    control = cfg.get("cycle", "control")
    poundctl = cfg.get("cycle", "poundctl")
    backends = cfg.get("cycle", "backends")
    backends = [x.strip().split(":") for x in backends.strip().split("\n")]
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
        print "sleep", grace
        time.sleep(grace)
        print stop
        os.system(stop)
        print start
        os.system(start)
        s = "poundctl -c %s -B 0 0 %d" % (control, i)
        print s
        os.system(s)
        
        
