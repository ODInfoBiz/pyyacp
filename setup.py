'''
Created on Dec 2, 2015

@author: jumbrich
'''

from setuptools import setup
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt", session=False)

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

files = ["resources/*"]

setup(name = "pyyacp",
    version = "0.1",
    description = "Yet Another CSV [Parser|Profiler]",
    author = "Juergen Umbrich, Sebastian Neumaier, Nina Mrzeli, Michael Undesser",
    author_email = "",
    url = "",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found 
    #recursively.)
    packages = ['pyyacp'],
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    package_data = {'csvengine' : files },
    #'runner' is in the root.
    #scripts = ["runner"],
    long_description = """""" ,
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []
    install_requires=reqs
) 
