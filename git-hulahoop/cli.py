#!/usr/bin/python3

import click


@click.group(help='Unnamed command line tool')
def cli():
    pass


@cli.group('issue', help='Handle issues')
def issue():
    pass


@issue.command()
def list():
    pass


if __name__ == '__main__':
    cli()
