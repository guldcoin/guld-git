#! /usr/bin/env python3
__version__ = '0.0.1'
import os
import argparse
from subprocess import check_output
# import pygit2
#from guldns import cfg.rawpath, cfg.username, cfg.username, BLOCKTREE
from guldcfg import BLOCKTREE, GuldConfig
#from pyolite import Pyolite
from camel_snake_kebab import kebab_case
import configparser
import os
cfg = GuldConfig()

#olite = Pyolite(admin_repository='%s/%s/.gitolite-admin' % (BLOCKTREE, ADMIN))

# TODO pull! check signatures! Do not decrypt or otherwise post-process
# TODO read version controlled files, guessing plaintext filenames, and include working/dirty files.

class Gitignore(object):
    """
    Functional gitignore parser.
    Reads 
    """

    def __init__(self, fh):
        self.fh = fh


    @property
    def toplevel():
        if not self._toplevel:
            self._toplevel = self.git("rev-parse", "--show-toplevel").splitlines()[-1]
        return self._toplevel

    @property
    def gitignore():
        if not self._gitignore:
            try:
                gi = open(os.path.join(self.get_toplevel(), '.gitignore'), 'r')
                self._gitignore = gi.readlines()
                gi.close()
            except:
                # TODO log this
                return None
        return self._gitignore


def getGuldHooks(gilines):
    # f = open('.gitignore', 'r')
    hooks = {}
    rules = []
    for line in gilines:#f.readlines():
        line = line.strip()
        if "#guld:" in line:
            rules = rules + line.replace("#guld:", "").split(":")
        else:
            if len(rules) != 0 and len(line) > 0:
                hooks[line.strip()] = rules
    return hooks


class Git(object):
    """
    This is a super hacky git wrapper. Uses subprocess instead of libgit2.
    TODO: port to C and use libgit2 directly
    """

    def __init__(self, path, user=cfg.username):
        self.user = user
        self.path = cfg.rawpath(path, self.user)
        self._toplevel = None
        self._gitignore = None
        self._gap = None

    @property
    def toplevel():
        if not self._toplevel:
            self._toplevel = self.git("rev-parse", "--show-toplevel").splitlines()[-1]
        return self._toplevel

    @property
    def gitignore():
        if not self._gitignore:
            try:
                gi = open(os.path.join(self.get_toplevel(), '.gitignore'), 'r')
                self._gitignore = gi.readlines()
                gi.close()
            except:
                # TODO log this
                return None
        return self._gitignore

    @property
    def gap():
        if not self._gap:
            self._gap = ConfigParser.ConfigParser()
            try:
                gi = open(os.path.join(self.get_toplevel(), '.gap.ini'), 'r')
                self._gap.readfp(gi)
                gi.close()
            except:
                # TODO log this
                return None
        return self._gap

    def git(self, cmd, *args, **kwargs):
        return check_output(['git', '-C', self.path, cmd] + list(args))

    def gitolite(self, cmd, *args, **kwargs):
        return check_output(['gitolite', '-C', self.path, cmd] + list(args))

    def getFiles(self):
        return self.git("ls-files", "--others", "--exclude-standard") #  | grep -o '\S*$'

    def getFingerprint(self, user=None):
        if user is None:
            return self.git("config", "user.signingkey").splitlines()[-1]
        # else:
        #     return check_output(["git", "config", "user.signingkey"], shell=True).splitlines()[-1]

    def pull(self, remote="origin", branch=None):
        if branch is None:
            branch = self.user
        return self.git("pull", remote, branch)

    def push(self, remote="origin", branch=None):
        if branch is None:
            branch = self.user
        return self.gitolite("push", remote, branch)

    def addAll(self):
        return self.git("add", "-A")

    def add(self, path):
        return self.git("add", path)

    def commit(self, message):
        return self.git("commit", "-m", message)

    def stash(self, args):
        return self.git("stash", list(args))

    def checkout(self, branch=None):
        if branch is None:
            branch = self.user
        return self.git("checkout", '-b', branch)

    def init(self):
        lpath = self.path.replace(BLOCKTREE, '')
        kpath = kebab_case(lpath)
        self.git("init")
        self.git("remote", "add", "origin",
            BLOCKTREE + "/git/repositories/%s.git" % lpath)
        self.checkout()
        repo = olite.repos.get_or_create(kpath)
        repo.users.add(olite.users.get(self.user), permission='RW+')
        # repo.users.add(olite.users.get("%s-group" % self.user), permission='R')


def main():
    parser = argparse.ArgumentParser('guld-git')
    parser.add_argument("command", type=str, default="get", choices=["push", "pull"])
    parser.add_argument("account", type=str, help="The account to run command on.")
    args = parser.parse_args()
    if args.command == 'get':
        print(get_pass(args.account))
    elif args.command == 'generate':
        print(generate_pass(args.account))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

