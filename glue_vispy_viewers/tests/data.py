"""
Fetcher for real test datasets from glue-example-data.

This is a near-copy of ``glue_jupyter.data.require_data`` with a small
on-disk cache added so repeated test runs don't re-download. The intent
is to move this upstream to glue-core eventually so every package in the
glue ecosystem can use one fetcher.
"""

import os
from functools import lru_cache
from urllib.request import urlopen


__all__ = ['require_data']


DATA_REPO = "https://raw.githubusercontent.com/glue-viz/glue-example-data/master/"


def _default_cache_dir():
    return os.path.join(os.path.expanduser('~'), '.cache', 'glue-example-data')


@lru_cache(maxsize=None)
def require_data(file_path, cache_dir=None):
    """
    Download ``file_path`` from glue-example-data and return the local path.

    The download is cached to ``cache_dir`` (defaults to
    ``~/.cache/glue-example-data``), so successive calls return the
    cached path without re-downloading. The in-process ``lru_cache``
    means we don't even ``stat`` the file again within a single session.
    """
    cache_dir = cache_dir or _default_cache_dir()
    os.makedirs(cache_dir, exist_ok=True)
    local_path = os.path.join(cache_dir, file_path.split('/')[-1])
    if not os.path.exists(local_path):
        with urlopen(DATA_REPO + file_path, timeout=60) as request:
            with open(local_path, 'wb') as f:
                f.write(request.read())
    return local_path
