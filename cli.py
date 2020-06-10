import click
import logging
from pathlib import Path


CLI_NAME = "gosh_sync"


def setup_logging(log_level):
    ext_logger = logging.getLogger(f"py.{CLI_NAME}")
    logging.captureWarnings(True)
    level = getattr(logging, log_level)
    logging.basicConfig(format="[%(asctime)s] %(levelname)s %(filename)s: %(message)s", level=level)
    if level <= logging.DEBUG:
        ext_logger.setLevel(logging.WARNING)


@click.group()
@click.option("-l", "--log-level", default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']))
def gosh_sync(log_level):
    setup_logging(log_level)


@gosh_sync.command()
@click.option("--log-dir", help="Output directory", required=True)
def sync_storage(log_dir):
    logger = logging.getLogger(f"py.{CLI_NAME}")
    logger.info(f'use pathlib to write to {log_dir}')

