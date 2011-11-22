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
import codecs
from Cheetah.Template import Template
from zc.buildout import easy_install

from util import PackageInstaller

class Interface(object):

    def __init__(self, interface, servername, port, ssl = None):
        self.interface = interface
        self.servername = servername
        self.port = port
        self.ssl = ssl

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
        self.options.setdefault('namevirtualhost', self.options['listen'])
        self.options.setdefault('sslca', '')

        if self.options.get("enhanced-privacy", None):
            options.setdefault("logformat", '"0.0.0.0 %l %u %t \\"%r\\" %>s %b \\"%{Referer}i\\" \\"%{User-agent}i\\""')
        else:
            options.setdefault("logformat", "Combined")
            
    def install(self):
        outputdir = os.path.join(self.buildout['buildout']['directory'], self.name)
        htdocs = self.options['htdocs']
        if not os.path.exists(outputdir):
            os.mkdir(outputdir)
        if os.path.exists(htdocs):
            shutil.rmtree(htdocs)
        packager = PackageInstaller(self)
        self.options['path'] = packager.package_path(self.options['path'])
        shutil.copytree(self.options['path'], htdocs)
        for file in self.options["substitute"].strip().split():
            tpt = codecs.open(os.path.join(self.options['path'], file), "r", "utf-8").read()
            t = Template(tpt, searchList={'baseurl': self.options['public']})
            codecs.open(os.path.join(htdocs, file), "w", "utf-8").write(unicode(t))
        vars = self.options.copy()
        vars.update({
            'listen': self.options['listen'] == 'yes',
            'namevirtualhost': self.options['namevirtualhost'] == 'yes',
            'interfaces': [Interface(*x.split(":")) for x in self.options['interfaces'].strip().split()],
        })
        t = Template(open(self.options['template']).read(), searchList=vars)
        open(self.options['output'], "w").write(str(t))
        return [outputdir]

    def update(self):
        pass    

