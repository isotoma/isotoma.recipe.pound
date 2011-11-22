import os
from zc.buildout import easy_install

class PackageInstaller:
    
    def __init__(self, original):
        self.original = original
        
    
    def install(self, *distributions):
        buildout = self.original.buildout
        python = buildout['buildout']['python']
        executable = buildout[python]['executable']
        if 'find-links' in buildout['buildout']:
            links = buildout['buildout']['find-links'].split()
        else:
            links = ()
        index = buildout.get('index', None)
        if buildout.get('offline') != 'true':
            easy_install.install(
                distributions,
                buildout['buildout']['eggs-directory'],
                links=links,
                index=index,
                executable=executable,
                always_unzip=True,
                path=[buildout['buildout']['develop-eggs-directory']],
                newest=buildout.get('newest', 'false') == 'true',
                )
        
    def package_path(self, path):
        """ Convert a package path to the real path on disk. A package path resembles:
        
            package://<package name>/<path>
            
        And refers to the path within the named python package.
        
        """
    
        if not path.startswith("package://"):
            return path
        package, subpath = path[10:].split("/", 1)
        self.install(package)
        init = __import__(package, fromlist=['foo']).__file__
        root = "/".join(init.split("/")[:-1])
        realpath = os.path.join(root, subpath)
        return realpath

