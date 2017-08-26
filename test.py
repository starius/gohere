#!/usr/bin/env python

import logging
import os
import platform
import shutil
import subprocess

import gohere

def run(args, env=None):
    logging.info('Running %s', ' '.join(args))
    process = subprocess.Popen(args, env=env)
    process.communicate()
    assert process.returncode == 0

logging.basicConfig(level=logging.DEBUG)

# race doesn't work on Windows:
# https://ci.appveyor.com/project/starius/gohere/build/1.0.36
# On OSX it takes too much time to build in Travis:
# https://travis-ci.org/starius/gohere/jobs/236756315
race = (platform.system() == 'Linux')

def latestMajor(version):
    version = gohere.version_tuple(version)
    for other in gohere.VERSIONS:
        other = gohere.version_tuple(other)
        if version[:2] == other[:2] and other > version:
            return False
    return True

for version in sorted(gohere.VERSIONS, key=gohere.version_tuple):
    if not latestMajor(version):
        continue

    goroot = 'goroot%s' % version
    gopath = 'gopath%s' % version
    if os.path.exists(goroot):
        shutil.rmtree(goroot)
    if os.path.exists(gopath):
        shutil.rmtree(gopath)

    # install
    gohere.gohere(
        goroot,
        version,
        race=race,
    )

    # build racesync
    gohere.mkdir_p(gopath)
    go_binary = os.path.join(goroot, 'bin', 'go')
    args = [go_binary, 'get', 'github.com/starius/racesync']
    if race:
        args = [go_binary, 'get', '-race', 'github.com/starius/racesync']
    env = os.environ.copy()
    env['GOPATH'] = os.path.abspath(gopath)
    # see https://github.com/travis-ci/travis-ci/issues/6388
    env.pop('GOROOT', None)
    run(args, env)

    # run racesync
    hello_binary = os.path.join(gopath, 'bin', 'racesync')
    args = [hello_binary]
    run(args)
