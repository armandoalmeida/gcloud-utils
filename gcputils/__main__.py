"""-----------------------
Google Cloud Utilities
-----------------------
Version: {__version__}
"""

from . import __version__


def main(*args, **kwargs):
    print(__doc__.replace('{__version__}', __version__))


if __name__ == "__main__":
    main()
