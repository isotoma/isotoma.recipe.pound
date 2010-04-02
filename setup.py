from setuptools import setup, find_packages

version = '0.0.0'

setup(
    name = 'isotoma.recipe.pound',
    version = version,
    description = "Buildout recipes to configure the pound load balancer",
    long_description = open("README.rst").read() + "\n" + \
                       open("CHANGES.txt").read(),
    classifiers = [
        "Framework :: Buildout",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords = "proxy buildout pound",
    author = "Doug Winter",
    author_email = "doug.winter@isotoma.com",
    license="Apache Software License",
    packages = find_packages(exclude=['ez_setup']),
    package_data = {
        '': ['README.rst', 'CHANGES.txt'],
        'isotoma.recipe.pound': ['pound.cfg', 'apache.conf']
    },
    namespace_packages = ['isotoma', 'isotoma.recipe'],
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'setuptools',
        'zc.buildout',
        'Cheetah',
        'isotoma.recipe.gocaptain',
    ],
    entry_points = {
        "zc.buildout": [
            "default = isotoma.recipe.pound:Pound",
            "emergency = isotoma.recipe.pound.emergency:Emergency",
        ],
    }
)
