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
        return False

    script_module = MODULES[args.script]
    result = True
    try:
        db = create_db(_db=_db)
        result = script_module.main(db, argv)
    finally:
        if _db is None:  # pragma: no cover
            db.close()
    return result


def console_entry():  # pragma: no cover
    configure_logging()
    result = main(sys.argv)
    sys.exit(int(not result))
