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

def test_installation(version, goroot, gopath, race1):
    # build racesync
    gohere.mkdir_p(gopath)
    go_binary = os.path.join(goroot, 'bin', 'go')
    args = [go_binary, 'get', 'github.com/starius/racesync']
    if gohere.version_tuple(version) >= gohere.version_tuple('1.18'):
        args = [go_binary, 'install', 'github.com/starius/racesync@latest']
    if race1:
        args.append('-race')
    env = os.environ.copy()
    env['GOPATH'] = os.path.abspath(gopath)
    # see https://github.com/travis-ci/travis-ci/issues/6388
    env.pop('GOROOT', None)
    run(args, env)
    # run racesync
    hello_binary = os.path.join(gopath, 'bin', 'racesync')
    args = [hello_binary]
    run(args)

for version in sorted(gohere.VERSIONS, key=gohere.version_tuple):
    if not latestMajor(version):
        continue
    if platform.system() == 'Darwin' and gohere.version_tuple(version) < gohere.version_tuple('1.7.6'):
        continue
    if gohere.version_tuple(version) < gohere.version_tuple('1.19') and gohere.version_tuple(version)[1] % 2 == 0:
        # Test only odd major versions before 1.19.
        continue
    race1 = race and 'bootstrap' not in version
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
        race=race1,
    )
    test_installation(version, goroot, gopath, race1)

for version in ['1.5.4', max(gohere.VERSIONS, key=gohere.version_tuple)]:
    if platform.system() == 'Windows':
        continue
    if platform.system() == 'Darwin' and gohere.version_tuple(version) < gohere.version_tuple('1.7.6'):
        continue
    race1 = race and 'bootstrap' not in version
    goroot = 'test_goroot%s' % version
    gopath = 'test_gopath%s' % version
    if os.path.exists(goroot):
        shutil.rmtree(goroot)
    if os.path.exists(gopath):
        shutil.rmtree(gopath)
    lines = []
    gohere.gohere(
        None,
        version,
        race=race1,
        echo=lines.append,
    )
    shell = '\n'.join(lines)
    script = './run.sh'
    with open(script, 'w') as f:
        f.write(shell)
    run(['chmod', '+x', script])
    run([script, goroot])
    test_installation(version, goroot, gopath, race1)
