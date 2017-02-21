git-hulahoop
============

git **Hu**b/**La**b/**Ho**me server **op**eration utility.

Currently only does issues and only on GitLab (since that is all I needed when I wrote it). Feel free to extend!


Example
-------

1. Configure (`.gitconfig`):


[git-hulahoop "my.gitlab.server.com"]
    token = "..."
[alias]
    issue = hulahoop issue

2. Go to any repo and list issues:

```
$ git hulahoop issue list
```

You can use just `git issue` if the alias is setup correctly. To create a new issue:

```
$ git issue new -m 'A new issue. With a detailed description.'
```

See `git issue new --help` for details on how to enter titles and bodies.
