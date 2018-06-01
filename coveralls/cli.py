"""Publish coverage results online via coveralls.io

Puts your coverage results on coveralls.io for everyone to see.

This tool makes custom reports for data generated by coverage.py package and
sends it to the coveralls.io service API.

All Python files in your coverage analysis are posted to this service along
with coverage stats, so please make sure you're not ruining your own security!

Usage:
    coveralls [options]
    coveralls debug [options]

    Debug mode doesn't send anything, just outputs json to stdout. It also
    forces verbose output. Please use debug mode when submitting bug reports.

Global options:
    --service=<name>  Provide an alternative service name to submit.
    --rcfile=<file>   Specify configuration file. [default: .coveragerc]
    --output=<file>   Write report to file. Doesn't send anything.
    --merge=<file>    Merge report from file when submitting.
    -h --help         Display this help.
    -v --verbose      Print extra info, always enabled when debugging.

Example:
    $ coveralls
    Submitting coverage to coveralls.io...
    Coverage submitted!
    Job #38.1
    https://coveralls.io/jobs/92059
"""
import logging
import sys

import docopt

from .api import Coveralls
from .exception import CoverallsException
from .version import __version__


log = logging.getLogger(__name__)


def main(argv=None):
    options = docopt.docopt(__doc__, argv=argv, version=__version__)
    if options['debug']:
        options['--verbose'] = True

    level = logging.DEBUG if options['--verbose'] else logging.INFO
    log.addHandler(logging.StreamHandler())
    log.setLevel(level)

    try:
        token_required = not options['debug'] and not options['--output']
        coverallz = Coveralls(token_required,
                              config_file=options['--rcfile'],
                              service_name=options['--service'])

        if options['--merge']:
            coverallz.merge(options['--merge'])

        if options['debug']:
            log.info('Testing coveralls-python...')
            coverallz.wear(dry_run=True)
        elif options['--output']:
            log.info('Write coverage report to file...')
            coverallz.save_report(options['--output'])
        else:
            log.info('Submitting coverage to coveralls.io...')
            result = coverallz.wear()
            log.info('Coverage submitted!')
            log.debug(result)
            log.info(result['message'])
            log.info(result['url'])
    except KeyboardInterrupt:  # pragma: no cover
        log.info('Aborted')
    except CoverallsException as e:
        log.exception(e)
        sys.exit(1)
    except KeyError as e:  # pragma: no cover
        log.exception(e)
        sys.exit(2)
