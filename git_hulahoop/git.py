import re
import os
import subprocess

import gitlab

_URL_RE = re.compile('.*?@(.*?):(.*)')


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

    def get_issues(self):
        issues = self.project.issues.list()
        return issues


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
