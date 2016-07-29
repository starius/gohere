#!/usr/bin/env python

""" Install Go into a local directory. """

import argparse
import hashlib
import logging
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
try:
    import urllib2
except:
    # Python 3
    import urllib.request as urllib2


VERSIONS = {
    '1.4.3': '9947fc705b0b841b5938c48b22dc33e9647ec0752bae66e50278df4f23f64959',
    '1.6.2': '787b0b750d037016a30c6ed05a8a70a91b2e9db4bd9b1a2453aa502a63f1bccc',
}
BOOTSTRAP_VERSION = '1.4.3'
MIN_VERSION_BUILT_WITH_GO = '1.5.0'

class TempDir(object):
    def __enter__(self):
        self.name = tempfile.mkdtemp()
        return self.name

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.name)

def version_tuple(version):
    return tuple(map(int, (version.split('.'))))

def is_build_with_go(version):
    return version_tuple(version) >= version_tuple(MIN_VERSION_BUILT_WITH_GO)

def get_default_cache():
    # based on hererocks.py
    if os.name == 'nt':
        cache_root = os.getenv('LOCALAPPDATA')
        if cache_root is None:
            cache_root = os.getenv('USERPROFILE')
            if cache_root is None:
                return None
            cache_root = os.path.join(cache_root, 'Local Settings', 'Application Data')
        return os.path.join(cache_root, 'GoHere', 'Cache')
    else:
        home = os.path.expanduser('~')
        if home == '~':
            return None
        else:
            return os.path.join(home, '.cache', 'gohere')

def get_filename(version):
    return 'go%s.src.tar.gz' % version

def get_url(version):
    return 'https://storage.googleapis.com/golang/%s' % get_filename(version)

def download_file(destination, url):
    with open(destination, 'wb') as d:
        request =  urllib2.urlopen(url)
        shutil.copyfileobj(request, d)
        request.close()
        logging.info('File %s was downloaded from %s', destination, url)

def make_checksum(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 ** 2), b''):
            hasher.update(chunk)
    value = hasher.hexdigest()
    logging.info('sha256(%s) = %s', filepath, value)
    return value

def test_checksum(filename, version):
    expected_checksum = VERSIONS[version]
    observed_checksum = make_checksum(filename)
    if expected_checksum == observed_checksum:
        logging.info('Checksum of %s is good', filename)
    else:
        logging.error(
            'Checksum of %s is bad.\nExpected %s,\nobserved %s.',
            filename,
            expected_checksum,
            observed_checksum,
        )
        sys.exit(1)

def unpack_file(parent_of_goroot, archive_name):
    with tarfile.open(archive_name, 'r:gz') as archive:
        archive.extractall(parent_of_goroot)
        logging.info('File %s was unpacked to %s', archive_name, parent_of_goroot)

def build_go(goroot_final, goroot, goroot_bootstrap):
    args = ['./make.bash']
    env = os.environ.copy()
    env['GOROOT_FINAL'] = goroot_final
    if goroot_bootstrap:
        env['GOROOT_BOOTSTRAP'] = goroot_bootstrap
        logging.info('Building with Go bootstrap from %s', goroot_bootstrap)
    cwd = os.path.join(goroot, 'src')
    go_process = subprocess.Popen(args, cwd=cwd, env=env)
    go_process.communicate()
    if go_process.returncode != 0:
        logging.error('Failed to build Go.')
        sys.exit(1)
    logging.info('Go was built in %s', goroot)

def install_go(goroot_final, goroot):
    if not os.path.exists(goroot_final):
        os.mkdir(goroot_final)
    for subdir in ('include', 'src', 'bin', 'pkg'):
        src = os.path.join(goroot, subdir)
        if subdir == 'include' and not os.path.exists(src):
            continue # TODO: absent in Go 1.6.2
        dst = os.path.join(goroot_final, subdir)
        shutil.copytree(src, dst)
    logging.info('Go was installed to %s', goroot_final)

def get_from_cache_or_download(cache_root, version, tmp_dir):
    filename = get_filename(version)
    if cache_root:
        file_in_cache = os.path.join(cache_root, filename)
        if os.path.isfile(file_in_cache):
            test_checksum(file_in_cache, version)
            logging.info('Reusing file from cache: %s', file_in_cache)
            return file_in_cache
    tmp_name = os.path.join(tmp_dir, filename)
    download_file(tmp_name, get_url(version))
    test_checksum(tmp_name, version)
    if cache_root:
        if not os.path.exists(cache_root):
            os.mkdir(cache_root)
        os.rename(tmp_name, file_in_cache)
        logging.info('New file was added to cache: %s', file_in_cache)
        return file_in_cache
    else:
        return tmp_name

def make_goroot_bootstrap(cache_root, tmp_dir):
    subdir = 'go%s_bootstrap' % BOOTSTRAP_VERSION
    if cache_root:
        goroot_bootstrap = os.path.join(cache_root, subdir)
        if os.path.exists(goroot_bootstrap):
            logging.info('Reusing bootstrap Go from %s', goroot_bootstrap)
            return goroot_bootstrap
    else:
        goroot_bootstrap = os.path.join(tmp_dir, subdir)
    logging.info('Building Go bootstrap in %s', goroot_bootstrap)
    gohere(goroot_bootstrap, BOOTSTRAP_VERSION, cache_root)
    logging.info('Go bootstrap was built in %s', goroot_bootstrap)
    return goroot_bootstrap

def gohere(
    goroot,
    version,
    cache_root,
):
    if os.path.exists(goroot):
        logging.error('%s already exists. Remove it manually', goroot)
        sys.exit(1)
    goroot_bootstrap = None
    with TempDir() as tmp_dir:
        if is_build_with_go(version):
            logging.info('Go bootstrap is needed for Go %s', version)
            goroot_bootstrap = make_goroot_bootstrap(cache_root, tmp_dir)
            logging.info('Using Go bootstrap in %s', goroot_bootstrap)
        archive = get_from_cache_or_download(cache_root, version, tmp_dir)
        unpack_file(tmp_dir, archive)
        goroot_build = os.path.join(tmp_dir, 'go')
        build_go(goroot, goroot_build, goroot_bootstrap)
        install_go(goroot, goroot_build)
        logging.info('Go was built and installed to %s', goroot)

def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        'goroot',
        type=str,
        help='Root of Go',
    )
    parser.add_argument(
        '--version',
        type=str,
        help='Go version',
        default='1.6.2',
    )
    parser.add_argument(
        '--cache',
        type=str,
        help='Cache for downloaded Go sources',
        default=get_default_cache(),
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    gohere(
        args.goroot,
        args.version,
        args.cache,
    )

if __name__ == '__main__':
    main()
