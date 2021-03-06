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

from zc.buildout import easy_install

class Cycle(object):

    def __init__(self, buildout, name, options):
        self.name = name
        self.buildout = buildout
        self.options = options
        self.options.setdefault("grace", "30")
        self.options.setdefault('control', os.path.join(self.buildout['buildout']['directory'], "var", "%s.ctl" % self.name))
        self.options.setdefault('poundctl', "/usr/sbin/poundctl")
        self.options.setdefault('wakeup', '')

    def install(self):
        outputdir = os.path.join(self.buildout['buildout']['parts-directory'], self.name)
        if not os.path.exists(outputdir):
            os.mkdir(outputdir)
        self.options.created(outputdir)

        self.ininame = os.path.join(outputdir, "cycle.ini")
        ini = open(self.ininame, "w")
        print >>ini, "[cycle]"
        print >>ini, "grace = %s" % (self.options['grace'],)
        print >>ini, "control = %s" % (self.options['control'],)
        print >>ini, "poundctl = %s" % (self.options['poundctl'],)
        print >>ini, "backends = %s" % "\n    ".join(self.options.get_list('backends'))
        print >>ini, "wakeup = %s" % "\n    ".join(self.options.get_list('wakeup'))

        self.make_wrapper()

        return self.options.created()

    def make_wrapper(self):
        path = self.buildout["buildout"]["bin-directory"]
        egg_paths = [
            self.buildout["buildout"]["develop-eggs-directory"],
            self.buildout["buildout"]["eggs-directory"],
            ]
        arguments = "'%s'" % self.ininame

        ws = easy_install.working_set(["isotoma.recipe.pound"], sys.executable, egg_paths)
        easy_install.scripts([(self.name, "isotoma.recipe.pound.cyclescript", "execute")], ws, sys.executable, path, arguments=arguments)
        self.options.created(os.path.join(path, self.name))

    def update(self):
        pass


