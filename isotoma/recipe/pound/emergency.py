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
import shutil
from Cheetah.Template import Template

class Interface(object):

    def __init__(self, interface, servername, port):
        self.interface = interface
        self.servername = servername
        self.port = port

class Emergency(object):

    def __init__(self, buildout, name, options):
        self.name = name
        self.buildout = buildout
        self.options = options
        outputdir = os.path.join(self.buildout['buildout']['directory'], self.name)
        htdocs = os.path.join(outputdir, 'htdocs')
        self.options.setdefault('htdocs', htdocs)
        self.options.setdefault('path', 'emergency')
        self.options.setdefault('output', os.path.join(outputdir, "apache.conf"))
        self.options.setdefault('access_log', os.path.join(outputdir, "access.log"))
        self.options.setdefault('error_log', os.path.join(outputdir, "error.log"))
        self.options.setdefault('template', os.path.join(os.path.dirname(__file__), "apache.conf"))
        self.options.setdefault('listen', 'no')

    def install(self):
        outputdir = os.path.join(self.buildout['buildout']['directory'], self.name)
        htdocs = self.options['htdocs']
        if not os.path.exists(outputdir):
            os.mkdir(outputdir)
        if os.path.exists(htdocs):
            shutil.rmtree(htdocs)
        shutil.copytree(self.options['path'], htdocs)
        for file in self.options["substitute"].strip().split():
            tpt = open(os.path.join(self.options['path'], file)).read()
            t = Template(tpt, searchList={'baseurl': self.options['public']})
            open(os.path.join(htdocs, file), "w").write(str(t))
        vars = self.options.copy()
        vars.update({
            'listen': self.options['listen'] == 'yes',
            'interfaces': [Interface(*x.split(":")) for x in self.options['interfaces'].strip().split()],
        })
        t = Template(open(self.options['template']).read(), searchList=vars)
        open(self.options['output'], "w").write(str(t))
        return [outputdir]

    def update(self):
        pass    

