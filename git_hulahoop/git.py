import re
import os
import subprocess

import gitlab

_URL_RE = re.compile('.*?@(.*?):(.*)')


class Issue(object):
    def __init__(self, id, title=None, url=None, desc=None):
        self.id = id
        self.title = title
        self.url = url
        self.desc = desc

    @property
    def comments(self):
        if not hasattr(self, '_comments'):
            raise RuntimeError('Comments not retrieved')
        return self._comments

    def __str__(self):
        return '#{}: {}'.format(self.id, self.title)


class Comment(object):
    def __init__(self, id, body, author=None, author_full=None):
        self.id = id
        self.body = body
        self.author = author
        self.author_full = author_full


class GitConfig(object):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def __getitem__(self, key):
        raw = subprocess.check_output(
            ['git', 'config', '--get', key],
            cwd=self.repo_path)

        return raw.rstrip(b'\n').decode('utf8')


class GitManager(object):
    pass


class GitLabManager(object):
    def __init__(self, repo):
        self._api = None
        self._project = None

        self.repo = repo

        # get token
        self.token = self.repo.config['git-hulahoop.{}.token'.format(
            self.repo.host)]

    @property
    def api(self):
        if not self._api:
            self._api = gitlab.Gitlab('https://{}'.format(self.repo.host),
                                      self.token)
        return self._api

    @property
    def project(self):
        if not self._project:
            self._project = self.api.projects.get(self.repo.url_path.rstrip(
                '.git'))
        return self._project

    def _make_issue(self, api_issue):
        return Issue(api_issue.iid, api_issue.title, api_issue.web_url,
                     api_issue.description)

    def _make_comment(self, api_note):
        return Comment(api_note.id,
                       api_note.body,
                       api_note.author.username,
                       api_note.author.name, )

    def get_issue_by_id(self, id, with_comments=True):
        issues = self.project.issues.list(iid=id)

        if not issues:
            return None

        assert len(issues) == 1

        issue = self._make_issue(issues[0])

        if with_comments:
            issue._comments = [
                self._make_comment(note)
                for note in sorted(issues[0].notes.list(),
                                   key=lambda n: -n.id)
            ]

        return issue

    def get_issues(self, open_only=True):
        kwargs = {}
        if open_only:
            kwargs['state'] = 'opened'

        issues = self.project.issues.list(**kwargs)

        return [self._make_issue(i) for i in issues]

    def create_issue(self, title, description):
        return self._make_issue(self.project.issues.create(
            {'title': title,
             'description': description}))

    def add_comment_to_issue(self, id, body):
        issue = self.project.issues.list(iid=id)[0]
        issue.notes.create({'body': body})


class GitRepo(object):
    def __init__(self, path, remote, host, remote_type):
        self.path = path
        self.remote = remote

        # FIXME: use filesystem locale
        self.repo_path = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=path).decode('UTF-8').rstrip()

        # FIXME: handle bare repositories
        self.git_path = os.path.join(self.repo_path, '.git')

        self.config = GitConfig(self.repo_path)
        self.remote_url = subprocess.check_output(
            ['git', 'config', '--get', 'remote.{}.url'.format(self.remote)
             ]).decode('UTF-8').rstrip()

        # FIXME: proper URL handling is hard and not implemented yet. urllib
        # turned out to be less-than-satisfactory. sorry.

        m = _URL_RE.match(self.remote_url)

        if not m:
            raise ValueError('Did not understand remote URL {}'.format(
                self.remote_url))

        self.host = m.group(1)
        self.url_path = m.group(2)

        self.remote_type = remote_type
        if remote_type is 'auto':
            self.remote_type = 'gitlab'

        if self.remote_type == 'gitlab':
            self.manager = GitLabManager(self)
