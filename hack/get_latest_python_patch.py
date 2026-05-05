#!/usr/bin/python3
"""
Find the latest point release for a given Python minor version (e.g. 3.14)
by parsing https://www.python.org/ftp/python/
Validates that the source tarball actually exists (not just an RC directory).
Used at Docker build time to install the latest bugfix release.
"""
from html.parser import HTMLParser
import logging
import sys
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

URL = 'https://www.python.org/ftp/python/'


def find_best_python_version(release):
    class FindPythonVersions(HTMLParser):
        def __init__(self, release):
            super().__init__()
            self.release = release
            self.start = f'{release}.'
            self.candidates = []

        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                for name, value in attrs:
                    if name != 'href' or not value.startswith(self.start):
                        continue
                    suffix = value.removeprefix(self.start).rstrip('/')
                    if suffix.isdigit():
                        self.candidates.append(int(suffix))
                        return

    try:
        with urllib.request.urlopen(URL, timeout=30) as response:
            data = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        logger.error(f'HTTP error: {e.code} {e.reason}')
        sys.exit(1)
    except urllib.error.URLError as e:
        logger.error(f'URL error: {e.reason}')
        sys.exit(1)

    parser = FindPythonVersions(release)
    try:
        parser.feed(data)
    except Exception as e:
        logger.error(f'Cannot parse python versions for {release}: {e}')
        sys.exit(1)

    if not parser.candidates:
        logger.error(f'Cannot find python version for {release}')
        sys.exit(1)

    for patch in sorted(parser.candidates, reverse=True):
        tarball_url = f'{URL}{release}.{patch}/Python-{release}.{patch}.tgz'
        try:
            req = urllib.request.Request(tarball_url, method='HEAD')
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    print(patch)
                    return
        except (urllib.error.HTTPError, urllib.error.URLError):
            continue

    logger.error(f'No downloadable python tarball found for {release}')
    sys.exit(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) != 2:
        logger.error(f'Usage: {sys.argv[0]} <minor_version> (e.g. 3.14)')
        sys.exit(1)
    find_best_python_version(sys.argv[1])
