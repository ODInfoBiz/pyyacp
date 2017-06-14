'''
Created on Dec 2, 2015

@author: jumbrich
'''

from setuptools import setup, find_packages
from pip.req import parse_requirements

install_reqs = parse_requirements("requirements.txt", session=False)
reqs = [str(ir.req) for ir in install_reqs]

files = ["resources/*"]

setup(name = "pyyacp",
    version = "0.1",
    description = "Yet Another CSV [Parser|Profiler]",
    author = "Juergen Umbrich, Sebastian Neumaier, Nina Mrzeli, Michael Undesser, Maximilian Walz",
    author_email = "",
    url = "",
    packages = find_packages(exclude=['contrib', 'docs', 'tests*']),
    long_description = """""" ,
    install_requires=reqs
) 