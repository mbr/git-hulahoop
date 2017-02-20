#!/usr/bin/python3

import click

from .git import GitRepo


@click.group(help='Unnamed command line tool')
@click.option('-r',
              '--repo',
              default='.',
              type=click.Path(),
              help='Path to the repository to work on (default: .')
@click.option('-R',
              '--remote',
              default='origin',
              help='Remote to check for remote host (default: origin)')
@click.option('-T',
              '--remote-type',
              type=click.Choice(['auto', 'gitlab'], ),
              default='auto',
              help='API type to use')
@click.pass_context
def cli(ctx, repo, remote, remote_type):
    cfg = {'repo_path': repo, 'remote': remote, }
    ctx.obj = {'cfg': cfg, 'repo': GitRepo(repo, remote, None, remote_type), }


@cli.group('issue', help='Handle issues')
def issue():
    pass


@issue.command('list')
@click.pass_obj
def list_issues(obj):
    repo = obj['repo']

    for issue in repo.manager.get_issues():
        click.echo(issue)


if __name__ == '__main__':
    cli()
