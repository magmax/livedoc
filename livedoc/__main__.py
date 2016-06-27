import sys
import argparse
import logging
from livedoc import LiveDoc
from livedoc.reports import Report, ConsoleReporter, JunitReporter

from decorate import Decorate
import pkg_resources

logger = logging.getLogger(__name__)


def configure_logging(level):
    LOG_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG]
    log_level = LOG_LEVELS[min(level, len(LOG_LEVELS) - 1)]
    logging.basicConfig(
        level=log_level,
        format='[%(asctime)-15s] %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )


def main(args=None):
    parser = argparse.ArgumentParser(
        prog='livedoc',
        description='Generate Live Documentation',
    )
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
    parser.add_argument(
        '--junit-report',
        dest='junit_report',
        default=None,
        help="path to junit report output"
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help="Increase verbosity."
    )
    args = parser.parse_args(args or sys.argv[1:])
    configure_logging(args.verbose)
    decorator = Decorate(args.theme)
    decorator.add_css(
        pkg_resources.resource_filename('livedoc', 'assets/base.css')
    )
    decorator.add_js(
        pkg_resources.resource_filename('livedoc', 'assets/base.js')
    )
    report = Report()
    report.register(ConsoleReporter())
    if args.junit_report:
        report.register(JunitReporter(args.junit_report))
    livedoc = LiveDoc(decorator=decorator, report=report)
    livedoc.process(args.source, args.output)
    return livedoc.status

if __name__ == '__main__':  # NOQA
    sys.exit(main())
