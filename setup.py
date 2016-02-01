'''
Created on Dec 2, 2015

@author: jumbrich
'''

from setuptools import setup

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
    install_requires=[
        'structlog',
        'py-dateutil',
        'unicodecsv',
        'anycsv'
    ]     
) 