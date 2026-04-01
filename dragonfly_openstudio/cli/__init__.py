"""dragonfly-openstudio commands which will be added to the dragonfly cli"""
import click
from dragonfly.cli import main

from .translate import translate
from .simulate import simulate


@click.group(help='dragonfly openstudio commands.')
@click.version_option()
def openstudio():
    pass


# add sub-commands to openstudio
openstudio.add_command(translate)
openstudio.add_command(simulate)

# add openstudio sub-commands
main.add_command(openstudio)
