#!/usr/bin/python3

import sys

import click

from .git import GitRepo

NEW_ISSUE = """\
{title}{extra}
# Please enter the title and text message for your new issue. Enter an empty
# line to separate title and text.
#
# Lines with '#' will be ignored, and an empty message aborts the issue.
"""


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


@issue.command('new')
@click.option(
    '-m',
    '--message',
    default='',
    help=
    'Message for the new issue. Up until the first dot followed by a period '
    'is interpreted as title. If no message is given, an editor is launched.')
@click.option('-t',
              '--title-only',
              is_flag=True,
              default=False,
              help='Title-only.')
@click.option('-M', '--max-title-length', default=140)
@click.pass_obj
def new_issue(obj, message, title_only, max_title_length):
    title = ''
    body = ''

    if message:
        parts = message.split('. ', 1)
        title = parts.pop(0)
        if parts:
            body = parts.pop(0).lstrip()

    if not title or not (body or title_only):
        raw = click.edit(NEW_ISSUE.format(title=title,
                                          extra='\n\n' + body if body else ''))

        title = []
        body = []

        in_body = False

        if raw:
            for line in raw.splitlines():
                if line.startswith('#'):
                    continue

                if not in_body:
                    if not line.strip():
                        in_body = True
                        continue
                    title.append(line)
                    continue

                body.append(line)

        title = ' '.join(title)
        body = '\n'.join(body)

    click.echo('title: {}'.format(title))
    click.echo('body: {}'.format(body))

    if not (body or title_only):
        click.echo('No body entered.', err=1)
        sys.exit(1)

    if len(title) > max_title_length:
        click.echo('Title exceeds {} characters'.format(max_title_length),
                   err=1)
        sys.exit(1)

    # we've got a valid title and description, add issue

    repo = obj['repo']
    issue = repo.manager.create_issue(title, body)

    click.echo('{}'.format(issue))


if __name__ == '__main__':
    cli()
