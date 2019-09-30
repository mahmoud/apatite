
import re
from collections import Counter

import attr
from boltons.timeutils import isoparse
from boltons.dictutils import OMD

from apatite.utils import run_cap

required_cmds = {'git': 'install via your package manager'}

def collect(plist, project, repo_dir):
    vcs_name = project.clone_info[0]
    ret = {'vcs_name': vcs_name}
    if vcs_name == 'git':
        ret.update(get_git_info(repo_dir))
    return ret


@attr.s(cmp=False)
class Committer(object):
    names = attr.ib(default=attr.Factory(set))
    emails = attr.ib(default=attr.Factory(set))
    commit_count = attr.ib(default=0)

    def merged(self, other):
        ret = type(self)(names=set(self.names),
                         emails=set(self.emails),
                         commit_count=self.commit_count)
        ret.names.update(other.names)
        ret.emails.update(other.emails)
        ret.commit_count += other.commit_count
        return ret


class CommitterRegistry(object):
    """Built to handle the aliasing that occurs in git logs where the
    same person will appear with different names and emails, sometimes
    due to changes over time, sometimes due to committing from
    different environments, etc.

    Consolidates sets of names, emails, and commit counts down to
    unified identities the best we can.

    """
    def __init__(self):
        self._email_to_ident = {}
        self._name_to_ident = {}

    def register(self, name, email, count):
        norm_name = ' '.join(name.lower().split())
        norm_email = email.lower()  # TODO: maybe remove plus segments

        email_ident = self._email_to_ident.get(norm_email)
        name_ident = self._name_to_ident.get(norm_name)

        if name_ident == email_ident:
            ident = email_ident
        else:
            if name_ident is None:
                ident = email_ident
            elif email_ident is None:
                ident = name_ident
            else:
                ident = email_ident.merged(name_ident)
                for email in ident.emails:
                    self._email_to_ident[email] = ident
                for names in ident.names:
                    self._name_to_ident[name] = ident
        if ident is None:
            ident = Committer()
        ident.names.add(norm_name)
        self._name_to_ident[norm_name] = ident

        ident.emails.add(norm_email)
        self._email_to_ident[norm_email] = ident

        ident.commit_count += count
        return

    def get_committers(self):
        return sorted(set(self._email_to_ident.values()), key=lambda x: x.commit_count, reverse=True)


def _get_commit_dt(repo_dir, commit_hash, **kw):
    kw.setdefault('env', {})['TZ'] = 'UTC'
    kw['cwd'] = repo_dir
    proc_res = run_cap(['git', 'show', '-s', '--format=%cd', '--date=format-local:%Y-%m-%dT%H:%M:%S', commit_hash], **kw)
    date_text = proc_res.stdout.strip()
    return isoparse(date_text)


_git_committer_re = re.compile(r'^\s+(?P<commit_count>\d+)\s+(?P<name>.*)\s<(?P<email>[^>]*)>$', re.MULTILINE | re.UNICODE)

def get_git_info(repo_dir):
    ret = {}

    proc_res = run_cap(['git', 'rev-list', '--max-parents=0', 'HEAD'], cwd=repo_dir)
    first_commit_hashes = proc_res.stdout.strip().split()

    first_commit_dt = sorted([_get_commit_dt(repo_dir, fch) for fch in first_commit_hashes])[0]

    proc_res = run_cap(['git', 'rev-parse', 'HEAD'], cwd=repo_dir)
    latest_commit_hash = proc_res.stdout.strip()

    latest_commit_dt = _get_commit_dt(repo_dir, latest_commit_hash)

    ret['first_commit'] = first_commit_dt.isoformat()
    ret['latest_commit'] = latest_commit_dt.isoformat()

    proc_res = run_cap(['git', 'shortlog', '--summary', '--numbered', '--email'], cwd=repo_dir)

    committer_registry = CommitterRegistry()
    for match in _git_committer_re.finditer(proc_res.stdout):
        gdict = match.groupdict()
        gdict['commit_count'] = int(gdict['commit_count'])

        committer_registry.register(gdict['name'], gdict['email'], gdict['commit_count'])

    committers = committer_registry.get_committers()
    ret['commit_count'] = commit_count = sum([c.commit_count for c in committers])
    ret['committer_count'] = len(committers)  # redundant with committer_percent_dist.100

    # these will be stored as percentages, so keep it to two-digit precision max
    threshes = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
    commit_thresh_map = {thresh: (commit_count * thresh) for thresh in threshes}

    sorted_committers = sorted([(c, c.commit_count) for c in committers],
                               reverse=True, key=lambda x: x[1])
    def _get_proportion_count(thresh_commit_count):
        _cur_commit_count = 0
        _cur_committer_count = 0
        for committer, committer_commit_count in sorted_committers:
            if _cur_commit_count > thresh_commit_count:
                break
            _cur_commit_count += committer_commit_count
            _cur_committer_count += 1
        return _cur_committer_count

    # how many developers' commits does it take to comprise XX% of the commits?
    committer_dist_map = {round(thresh * 100): _get_proportion_count(thresh_commit_count)
                          for thresh, thresh_commit_count in commit_thresh_map.items()}
    ret['committer_percent_dist'] = committer_dist_map
    ret['committer_top_5'] = [round(c / commit_count, 4) for _, c in sorted_committers][:5]
    ret['minor_committer_counts'] = {x: len([c for _, c in sorted_committers if c <= x])
                                     for x in range(1, 6)}

    '''
    # DEBUG
    print(first_commit_dt.isoformat(), latest_commit_dt.isoformat(), latest_commit_dt - first_commit_dt)
    from pprint import pprint
    pprint(committer_dist_map)
    pprint(ret['top_5'])
    pprint(ret)
    raise SystemExit  # quits after the first
    '''
    return ret
