#!/usr/bin/env python

import logging
import os
import shutil
import subprocess

import gohere

def run(args, env=None):
    logging.info('Running %s', ' '.join(args))
    process = subprocess.Popen(args, env=env)
    process.communicate()
    assert process.returncode == 0

logging.basicConfig(level=logging.DEBUG)

for version in sorted(gohere.VERSIONS, key=gohere.version_tuple):
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
    )

    # build racesync
    gohere.mkdir_p(gopath)
    go_binary = os.path.join(goroot, 'bin', 'go')
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
