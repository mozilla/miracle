import argparse
import sys

from miracle.analysis import MODULES
from miracle.db import create_db
from miracle.log import (
    configure_logging,
    LOGGER,
)


def main(argv, _db=None):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description='Run an analysis script.')
    parser.add_argument('--script', required=True,
                        help='The analysis script to run.')

    # May raise SystemExit
    args = parser.parse_args(argv[1:])

    if args.script not in MODULES:
        LOGGER.info('Unknown analysis script. Choose one of:')
        LOGGER.info(', '.join(MODULES.keys()))
        return 1

    script_module = MODULES[args.script]
    try:
        db = create_db(_db=_db)
        LOGGER.info('Starting analysis.')
        script_module.main(db, argv)
        LOGGER.info('Finished analysis.')
    finally:
        if _db is None:  # pragma: no cover
            db.close()


def console_entry():  # pragma: no cover
    configure_logging()
    exit_code = main(sys.argv)
    if exit_code is not None:
        sys.exit(exit_code)
    sys.exit(0)
