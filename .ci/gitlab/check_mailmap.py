#!/usr/bin/env python3

import sys
from collections import defaultdict
from pathlib import Path
from subprocess import check_output

namesep = '??'
fmtsep = '||'
cmd = ['git', 'log', f'--format=%an{namesep}%ae{fmtsep}%aN{namesep}%aE']
seen_set = set()
seen = defaultdict(list)
for user in (f.split(fmtsep) for f in set(check_output(cmd, universal_newlines=True).strip().split('\n'))):
    if user[0] != user[1]:
        # has a mailmap entry
        continue
    name, email = user[0].split(namesep)
    seen_set.add((name, email))
    seen[name].append(email)

mailmap = Path(sys.argv[1]).resolve()
with open(mailmap) as f:
    contents = f.read()
# name is in mailmap, but email is new
missing = [(u, e) for u, e in seen_set if u in contents and e not in contents]
# name occurs with multiple mails, but no mailmap entry
duplicates = [(u, mails) for u, mails in seen.items() if len(mails) > 1]

with open(mailmap) as f:
    lines = [l for l in f.readlines() if not l.startswith('#')]
for user, email in missing:
    print(f'missing mailmap entry for {user} {email}')
for user, emails in duplicates:
    print(f'multiple emails for {user}: {emails}')

sys.exit(len(missing) + len(duplicates))
