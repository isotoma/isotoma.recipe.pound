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
import os
import zc.buildout
from Cheetah.Template import Template
from isotoma.recipe import gocaptain

from util import PackageInstaller

try:
    from hashlib import sha1
except ImportError:
    import sha
    def sha1(str):
        return sha.new(str)

def sibpath(filename):
    return os.path.join(os.path.dirname(__file__), filename)

class Pound(object):

    template = os.path.join(os.path.dirname(__file__), "pound.cfg")

    def __init__(self, buildout, name, options):
        self.name = name
        self.options = options
        self.buildout = buildout
        self.outputdir = os.path.join(self.buildout['buildout']['parts-directory'], self.name)

        if not "pidfile" in self.buildout:
            if 'run-directory' in self.buildout['buildout']:
                self.options["pidfile"] = os.path.join(self.buildout['buildout']['run-directory'], "%s.pid" % self.name)
            else:
                self.options["pidfile"] = os.path.join(self.buildout['buildout']['directory'], "var", "%s.pid" % self.name)

        self.cfgfile = os.path.join(self.outputdir, "pound.cfg")
        self.options.setdefault('control', os.path.join(self.buildout['buildout']['directory'], "var", "%s.ctl" % self.name))
        self.options.setdefault('executable', '/usr/sbin/pound')
        self.options.setdefault('poundctl', '/usr/sbin/poundctl')
        self.options.setdefault('user', 'www-data')
        self.options.setdefault('group', 'www-data')
        self.options.setdefault('logfacility', 'local0')
        self.options.setdefault('loglevel', "2")
        self.options.setdefault('alive', "30")
        self.options.setdefault('timeout', "60")
        self.options.setdefault('xHTTP', "0")
        self.options.setdefault('template', sibpath("pound.cfg"))
        self.options["__hashes_template"] = sha1(open(self.options["template"]).read()).hexdigest()

    def install(self):
        if not os.path.isdir(self.outputdir):
            os.mkdir(self.outputdir)
        vars = {}
        for always in 'user', 'group', 'logfacility', 'loglevel', 'alive', 'timeout', 'address', 'port', 'xHTTP', 'control':
            vars[always] = self.options[always]
        if 'session' in self.options:
            # session seems to be restricted in Cheetah
            vars['affinity'] = dict(zip(['type', 'id', 'ttl'], self.options['session'].split(":", 2)))
        if 'emergency' in self.options:
            vars['emergency'] = dict(zip(['address', 'port'], self.options['emergency'].split(":", 1)))
        if 'err500' in self.options:
            packager = PackageInstaller(self)
            vars['err500'] = packager.package_path(self.options['err500'])
        vars['backends'] = []
        for l in self.options['backends'].split("\n"):
            l = l.strip()
            if l: vars['backends'].append(dict(zip(['address', 'port'], l.split(":", 1))))
        if not os.path.exists(self.outputdir):
            os.mkdir(self.outputdir)
        template = open(self.template).read()
        c = Template(template, searchList = vars)
        open(self.cfgfile, 'w').write(str(c))
        self.runscript()
        self.options.created(self.outputdir)
        target = os.path.join(self.buildout["buildout"]["bin-directory"],self.name + "ctl")
        poundctl = open(target, "w")
        print >> poundctl, "#!/bin/sh"
        print >> poundctl, "%s -c %s $*" % (self.options['poundctl'], self.options['control'])
        poundctl.close()
        os.chmod(target, 0755)
        self.options.created(target)
        return self.options.created()
        
    def runscript(self):
        target=os.path.join(self.buildout["buildout"]["bin-directory"],self.name)
        args = '-f "%s" -p "%s"' % (self.cfgfile, self.options["pidfile"])
        gc = gocaptain.Automatic()
        gc.write(open(target, "wt"), 
            daemon=self.options['executable'], 
            args=args, 
            pidfile=self.options["pidfile"], 
            name=self.name, 
            description="%s daemon" % self.name)
        os.chmod(target, 0755)
        self.options.created(target)
        
    def update(self):
        pass

