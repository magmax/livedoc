import argparse
import logging
from livedoc import LiveDoc

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)-15s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    )
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        'source',
        help='Path to be processed')
    parser.add_argument(
        '-o', '--output',
        default="output",
        help="Path to leave results"
    )
    args = parser.parse_args()
    livedoc = LiveDoc()
    livedoc.process(args.source, args.output)


if __name__ == '__main__':
    main()
