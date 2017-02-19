#!/usr/bin/python3

import click

from .git import GitRepo


@click.group(help='Unnamed command line tool')
@click.option('-r',
              '--repo',
              default='.',
              type=click.Path(),
              help='Path to the repository to work on (default: .')
@click.option(
    '-D',
    '--default-remote',
    default='origin',
    help='Remote to check for remote host if none given (default: origin')
@click.option('-R',
              '--remote',
              default=None,
              help='Remote to check for remote host')
@click.pass_context
def cli(ctx, repo, default_remote, remote):
    cfg = {'repo_path': repo,
           'default_remote': default_remote,
           'remote': remote, }
    ctx.obj = {'cfg': cfg, 'repo': GitRepo(repo, remote or default_remote), }


@cli.group('issue', help='Handle issues')
def issue():
    pass


@issue.command('list')
@click.pass_obj
def list_issues(obj):
    repo = obj['repo']
    click.echo('Host: {}'.format(repo.host))
    click.echo('obj: {}'.format(obj))
    pass


if __name__ == '__main__':
    cli()
