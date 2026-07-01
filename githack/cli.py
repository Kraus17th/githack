import argparse
import sys

from githack import __version__
from githack.scanner import Scanner

USAGE = """\
A `.git` folder disclosure exploit. By LiJieJie

Usage: githack http://www.target.com/.git/
"""


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="githack",
        description="Rebuild source code from an exposed .git folder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: githack http://www.target.com/.git/",
    )
    parser.add_argument("url", nargs="?", help="URL to the exposed .git folder")
    parser.add_argument(
        "-V", "--version", action="version", version="%(prog)s " + __version__
    )
    args = parser.parse_args(argv)

    if not args.url:
        print(USAGE)
        sys.exit(0)

    scanner = Scanner(args.url)
    scanner.scan()
    scanner.wait()


if __name__ == "__main__":
    main()
