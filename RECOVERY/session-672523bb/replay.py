import json, os, sys, re
ROOT = sys.argv[1]
EV = sys.argv[2]
ev = json.load(open(EV, encoding='utf-8'))['events']
starts = [e for e in ev if e['type'] == 'tool.execution_start' and e['data'].get('toolName') == 'apply_patch']
comp = {e['data'].get('toolCallId'): e for e in ev if e['type'] == 'tool.execution_complete'}
ok = fail = 0
failures = []

def read(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()

def write(p, s):
    os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(s)

def apply_update(text, hunks):
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.replace('\r\n', '\n').split('\n')
    pos = 0
    for h in hunks:
        old = [l[1:] for l in h if l[:1] in (' ', '-')]
        new = [l[1:] for l in h if l[:1] in (' ', '+')]
        if not old:
            lines[len(lines):] = new if lines and lines[-1] != '' else new
            continue
        idx = -1
        for start in (pos, 0):
            for i in range(start, len(lines) - len(old) + 1):
                if lines[i:i + len(old)] == old:
                    idx = i
                    break
            if idx >= 0:
                break
        if idx < 0:
            for start in (pos, 0):
                for i in range(start, len(lines) - len(old) + 1):
                    if [x.rstrip() for x in lines[i:i + len(old)]] == [x.rstrip() for x in old]:
                        idx = i
                        break
                if idx >= 0:
                    break
        if idx < 0:
            raise ValueError('hunk not found: ' + (old[0][:80] if old else ''))
        lines[idx:idx + len(old)] = new
        pos = idx + len(new)
    return nl.join(lines)

def parse(patch):
    ops = []
    cur = None
    for line in patch.split('\n'):
        if line.startswith('*** Begin Patch') or line.startswith('*** End Patch'):
            continue
        m = re.match(r'\*\*\* (Add|Update|Delete) File: (.*)', line)
        if m:
            cur = {'op': m.group(1), 'path': m.group(2).strip(), 'lines': [], 'move': None}
            ops.append(cur)
            continue
        m = re.match(r'\*\*\* Move to: (.*)', line)
        if m and cur:
            cur['move'] = m.group(1).strip()
            continue
        if cur is not None:
            cur['lines'].append(line)
    return ops

for e in starts:
    patch = e['data']['arguments']
    if isinstance(patch, dict):
        patch = patch.get('input') or json.dumps(patch)
    c = comp.get(e['data'].get('toolCallId'))
    try:
        for op in parse(patch):
            op['path'] = op['path'].replace('/workspaces/Unitary-Manifold-/wuzbak/Unitary-Manifold-/', '')
            if os.environ.get('ONLY') and not re.search(os.environ['ONLY'], op['path']):
                continue
            p = os.path.join(ROOT, op['path'])
            if op['op'] == 'Add':
                body = [l[1:] if l.startswith('+') else l for l in op['lines']]
                while body and body[-1] == '':
                    body.pop()
                write(p, '\n'.join(body) + '\n')
            elif op['op'] == 'Delete':
                if os.path.exists(p):
                    os.remove(p)
            else:
                hunks, cur = [], None
                for l in op['lines']:
                    if l.startswith('@@'):
                        cur = []
                        hunks.append(cur)
                    elif l == '' and cur is not None and l is op['lines'][-1]:
                        continue
                    else:
                        if cur is None:
                            cur = []
                            hunks.append(cur)
                        cur.append(l)
                text = read(p)
                out = apply_update(text, hunks)
                dest = os.path.join(ROOT, op['move']) if op['move'] else p
                write(dest, out)
                if op['move'] and os.path.exists(p):
                    os.remove(p)
        ok += 1
    except Exception as ex:
        fail += 1
        failures.append((e['timestamp'], str(ex)[:150], re.findall(r'\*\*\* (?:Add|Update|Delete) File: (.*)', patch)[:3]))
print('ok', ok, 'fail', fail)
for f in failures[:40]:
    print(f)
