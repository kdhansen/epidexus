import setuptools
from os import path

loc = path.abspath(path.dirname(__file__))

with open(loc + '/requirements.txt') as f:
    requirements = f.read().splitlines()

required = []
dependency_links = []
# do not add to required lines pointing to git repositories
EGG_MARK = '#egg='
for line in requirements:
    if line.startswith('-e git:') or line.startswith('-e git+') or \
            line.startswith('git:') or line.startswith('git+'):
        if EGG_MARK in line:
            package_name = line[line.find(EGG_MARK) + len(EGG_MARK):]
            required.append(package_name)
            dependency_links.append(line)
        else:
            print('Dependency to a git repository should have the format:')
            print('git+ssh://git@github.com/xxxxx/xxxxxx#egg=package_name')
    else:
        required.append(line)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="epidexus",
    version="0.3.0",
    author="Karl Damkjær Hansen",
    author_email="kdh@es.aau.dk",
    description="Agent-Based Simulation of Epidemics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kdhansen/epidexus",
    packages=setuptools.find_packages(),
    install_requires=required,
    dependency_links=dependency_links,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)