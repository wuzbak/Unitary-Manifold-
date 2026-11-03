import sys, os, re
sys.argv_backup = sys.argv
ROOT, PF = sys.argv[1], sys.argv[2]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'replay.py'), encoding='utf-8').read()
head = src.split("for e in starts:")[0]
head = head.replace("ROOT = sys.argv[1]", "ROOT = sys.argv[1]").replace(
    "ev = json.load(open(EV, encoding='utf-8'))['events']", "ev = []")
ns = {'__name__': 'x'}
sys.argv = [sys.argv[0], ROOT, 'unused']
exec(compile(head.replace("EV = sys.argv[2]", "EV = None"), 'replay_head', 'exec'), ns)
patch = open(PF, encoding='utf-8').read().replace('/workspaces/Unitary-Manifold-/wuzbak/Unitary-Manifold-/', '')
for op in ns['parse'](patch):
    p = os.path.join(ROOT, op['path'])
    if op['op'] == 'Add':
        body = [l[1:] if l.startswith('+') else l for l in op['lines']]
        while body and body[-1] == '':
            body.pop()
        ns['write'](p, '\n'.join(body) + '\n')
    elif op['op'] == 'Delete':
        if os.path.exists(p):
            os.remove(p)
    else:
        hunks, cur = [], None
        for l in op['lines']:
            if l.startswith('@@'):
                cur = []
                hunks.append(cur)
            elif l == '' and l is op['lines'][-1]:
                continue
            else:
                if cur is None:
                    cur = []
                    hunks.append(cur)
                cur.append(l)
        out = ns['apply_update'](ns['read'](p), hunks)
        dest = os.path.join(ROOT, op['move']) if op['move'] else p
        ns['write'](dest, out)
        if op['move'] and os.path.exists(p):
            os.remove(p)
    print('applied', op['op'], op['path'])
