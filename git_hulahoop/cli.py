#!/usr/bin/python3

import sys
import shutil
import subprocess

import click
import volatile

from .git import GitRepo


def mdv_print(md):
    with volatile.file(suffix='.md') as tmp:
        tmp.write(md.encode('utf8'))
        tmp.close()

        subprocess.check_call(['mdv', tmp.name])


NEW_ISSUE = """\
{title}{extra}
# Please enter the title and text message for your new issue. Enter an empty
# line to separate title and text.
#
# Lines with '#' will be ignored, and an empty message aborts the issue.
"""


@click.group(help='Repository manager tool')
@click.option(
    '-r',
    '--repo',
    default='.',
    type=click.Path(),
    help='Path to the repository to work on (default: .')
@click.option(
    '-R',
    '--remote',
    default='origin',
    help='Remote to check for remote host (default: origin)')
@click.option(
    '-T',
    '--remote-type',
    type=click.Choice(
        ['auto', 'gitlab'], ),
    default='auto',
    help='API type to use')
@click.option(
    '--mdv/--no-mdv',
    default=None,
    help='Enable mdv rendering (default: auto, depending on whether '
    'an executable named `mdv` is found on the path.')
@click.pass_context
def cli(ctx, repo, remote, remote_type, mdv):
    if mdv in (None, True):
        mdv = shutil.which('mdv')
    else:
        mdv = None

    cfg = {
        'repo_path': repo,
        'remote': remote,
    }
    ctx.obj = {
        'cfg': cfg,
        'repo': GitRepo(repo, remote, None, remote_type),
        'mdv': mdv
    }


@cli.group('issue', help='Handle issues')
def issue():
    pass


@issue.command('list')
@click.option(
    '--all',
    is_flag=True,
    default=False,
    help='Show all issues, not only open ones')
@click.pass_obj
def list_issues(obj, all):
    repo = obj['repo']

    for issue in repo.manager.get_issues(open_only=not all):
        click.echo(issue)


@issue.command('new')
@click.option(
    '-m',
    '--message',
    default='',
    help='Message for the new issue. Up until the first dot followed by a period '
    'is interpreted as title. If no message is given, an editor is launched.')
@click.option(
    '-T', '--title-only', is_flag=True, default=False, help='Title-only.')
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
        raw = click.edit(
            NEW_ISSUE.format(title=title, extra='\n\n' + body if body else ''))

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
        click.echo(
            'Title exceeds {} characters'.format(max_title_length), err=1)
        sys.exit(1)

    # we've got a valid title and description, add issue

    repo = obj['repo']
    issue = repo.manager.create_issue(title, body)

    click.echo('{}'.format(issue))


@issue.command('show')
@click.argument('ISSUE_NO', type=int)
@click.pass_obj
def show_issue(obj, issue_no):
    repo = obj['repo']

    issue = repo.manager.get_issue_by_id(issue_no)

    if not issue:
        click.echo('Issue #{} not found'.format(issue_no))
    else:
        md = ''
        # FIXME: finish that console util lib already!
        header = '#{}: {}'.format(issue_no, issue.title)
        md += header + '\n'
        md += '=' * len(header)
        md += '\n\n'
        md += issue.desc

        for comment in issue.comments:
            md += '\n\n---\n\n'
            # FIXME: escaping technically needed here
            md += '{} (*@{}*) commented:\n\n'.format(comment.author_full,
                                                     comment.author)
            md += comment.body + '\n'

        if obj['mdv']:
            mdv_print(md)
        else:
            click.echo(md)


if __name__ == '__main__':
    cli()


@issue.command('comment')
@click.argument('ISSUE_NO', type=int)
@click.option('-m', '--message', default='')
@click.pass_obj
def comment_issue(obj, issue_no, message):
    repo = obj['repo']

    issue = repo.manager.get_issue_by_id(issue_no)

    if not issue:
        click.echo('Issue #{} not found'.format(issue_no))
    else:
        if not message:
            message = click.edit('')

        if message is None:
            click.echo('No message entered')
            # FIXME: use proper CLI lib...
            return

        repo.manager.add_comment_to_issue(issue_no, message)
