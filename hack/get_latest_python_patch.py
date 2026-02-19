#!/usr/bin/python3
"""
Find the latest point release for a given Python minor version (e.g. 3.14)
by parsing https://www.python.org/ftp/python/
Used at Docker build time to install the latest bugfix release.
"""
from html.parser import HTMLParser
import sys
import urllib.request
import urllib.error

URL = 'https://www.python.org/ftp/python/'


def find_best_python_version(release):
    class FindPythonVersion(HTMLParser):
        def __init__(self, release):
            super().__init__()
            self.release = release
            self.start = f'{release}.'
            self.best_found_version = None

        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                try:
                    for name, value in attrs:
                        if name == 'href':
                            if value.startswith(self.start):
                                point = int(value.removeprefix(self.start).rstrip('/'))
                                if self.best_found_version is None or point > self.best_found_version:
                                    self.best_found_version = point
                                    return
                except Exception:
                    pass

        def get_best_version(self):
            return self.best_found_version

    try:
        with urllib.request.urlopen(URL) as response:
            data = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        print(f'HTTP error: {e.code} {e.reason}', file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f'URL error: {e.reason}', file=sys.stderr)
        sys.exit(1)

    parser = FindPythonVersion(release)
    try:
        parser.feed(data)
        if parser.get_best_version() is not None:
            print(parser.get_best_version())
        else:
            print(f'Cannot find python version for {release}', file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f'Cannot find python version for {release}: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <minor_version> (e.g. 3.14)', file=sys.stderr)
        sys.exit(1)
    find_best_python_version(sys.argv[1])
