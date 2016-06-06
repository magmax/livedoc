import argparse
import logging
from livedoc import LiveDoc
from decorate import Decorate
import pkg_resources

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)-15s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    )
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Generate Live Documentation')
    parser.add_argument(
        'source',
        help='Path to be processed')
    parser.add_argument(
        '-o', '--output',
        default="output",
        help="Path to leave results"
    )
    parser.add_argument(
        '-t', '--theme',
        default="bootstrap",
        help="Theme to be used."
    )
    args = parser.parse_args()
    decorator = Decorate(args.theme)
    decorator.add_css(
        pkg_resources.resource_filename('livedoc', 'assets/base.css')
    )
    decorator.add_js(
        pkg_resources.resource_filename('livedoc', 'assets/base.js')
    )
    livedoc = LiveDoc(decorator=decorator)
    livedoc.process(args.source, args.output)


if __name__ == '__main__':
    main()
