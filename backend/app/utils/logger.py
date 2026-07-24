"""
logger.py
---------
Configures application-wide logging so every module can `import logging`
and get consistent, readable log output (console + optional file).
"""

import logging
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
