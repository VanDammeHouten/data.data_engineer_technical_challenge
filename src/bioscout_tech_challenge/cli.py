import logging

from pyapp import app
from pyapp.app import CliApplication, argument, CommandOptions

APP = CliApplication()

main = APP.dispatch


@APP.command
@argument(
    "-n",
    "--name",
    help_text="Choose what name to greet",
    default="Nick",
)
def hello(opts: CommandOptions):
    logger = logging.getLogger(__name__)
    logger.info(f"Hello {opts.name}")
