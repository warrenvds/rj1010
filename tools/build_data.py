"""Build the dashboard data for one refresh.

  python3 build_data.py <export.xlsx|2025> <start YYYY-MM-DD> <out.json> [--through N] [--final] [--side DIR]

<export.xlsx>  Kobus's Strava export (sheet "Activities"). "2025" replays last year's results.
--through N    last complete day to show. Default: yesterday, counted from today's date (07:00 refresh).
--final        results are locked (after 07:00 on Saturday 12 December).
--side DIR     folder with the hand-kept files below. Default: ../data/<year> next to this script.
                 wagers.csv      no,wager,payer,amount   (payer = participant name as on Strava)
                 payments.csv    name,amount[,date,note] (one row per payment; repeats add up)
                 crews.csv       name,crew               (overrides the surname crews)
                 attendance.csv  day,name                (hosted-run attendance from the hosts)
Prints a report of anything skipped or unmatched so it can be checked before publishing.
"""
import sys, os, csv, json, re, argparse, datetime as dt
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
p = argparse.ArgumentParser()
p.add_argument('src'); p.add_argument('start'); p.add_argument('out')
p.add_argument('--through', type=int); p.add_argument('--final', action='store_true'); p.add_argument('--side')
p.add_argument('--target', type=int, default=100000); p.add_argument('--today')
A = p.parse_args()
start = dt.date.fromisoformat(A.start)
today = dt.date.fromisoformat(A.today) if A.today else dt.date.today()
base = json.load(open(os.path.join(HERE, 'data2025.json')))
TYPES = {'run': 'Run', 'trail run': 'Trail Run', 'treadmill': 'Treadmill', 'treadmill workout': 'Treadmill',
         'virtual run': 'Treadmill', 'walk': 'Walk', 'hike': 'Walk'}
report = []

def tidy(name):
    """Collapse spaces; fix words typed in ALL CAPS or all lower case (keeps 'van der', 'de')."""
    words = re.sub(r'\s+', ' ', str(name or '')).strip().split(' ')
    keep = {'van', 'der', 'de', 'du', 'le', 'la', 'von', 'da', 'dos'}
    out = []
    for i, w in enumerate(words):
        if (w.isupper() and len(w) > 1) or w.islower():
            w = w.lower() if (i and w.lower() in keep) else '-'.join(x[:1].upper() + x[1:].lower() for x in w.split('-'))
        out.append(w)
    return ' '.join(out)

def num(x):
    try: return float(str(x).replace('R', '').replace(',', '').strip())
    except (TypeError, ValueError): return None

def read(name):
    f = os.path.join(side, name)
    if not os.path.exists(f): return []
    with open(f, newline='', encoding='utf-8-sig') as fh: return [{k.strip().lower(): (v or '').strip() for k, v in r.items() if k} for r in csv.DictReader(fh)]

if A.src == '2025':
    year = 2025
    acts = [[a, d, k, 'Run', None, None, None] for a, d, k in base['runs']]
    wagers = [w for w in base['wagers'] if w['payer'] != 'All participants']
    payments = {}
    for r in csv.DictReader(open(os.path.join(HERE, 'participants_2025.csv'))) if os.path.exists(os.path.join(HERE, 'participants_2025.csv')) else []:
        if num(r.get('paid')): payments['Others' if r['athlete'].lower().startswith('other') else r['athlete']] = num(r['paid'])
    D = dict(base, acts=acts, year=2025, start='2026-12-01', window='Tuesday 1 to Thursday 10 December',
             through=10, final=True, wagers=wagers, payments=payments, crews={}, attendance={},
             note='Preview: these are the 2025 results replayed so you can see how the 2026 page will work. '
                  'Live 2026 results start on the morning of Wednesday 2 December, after Day 1.')
    side = A.side or os.path.join(HERE, '..', 'data', '2025')
    hs26 = os.path.join(HERE, '..', 'data', '2026', 'hosts.csv')
    if os.path.exists(hs26):
        with open(hs26, newline='', encoding='utf-8-sig') as fh: D['hosts'] = [{k: (v or 'TBC') if k in ('meeting_point', 'route', 'treats') else (v or '') for k, v in r.items()} for r in csv.DictReader(fh)]
else:
    import openpyxl
    year = start.year
    side = A.side or os.path.join(HERE, '..', 'data', str(year))
    ws = openpyxl.load_workbook(A.src, data_only=True)['Activities']
    rows = list(ws.iter_rows(values_only=True)); h = [str(c).strip() if c else c for c in rows[0]]
    need = {'athlete_name', 'activity_date', 'activity_type', 'distance_km', 'activity_id'}
    if need - set(h): sys.exit(f'Export is missing columns: {sorted(need - set(h))}')
    seen, raw, skip = set(), [], Counter()
    for r in rows[1:]:
        r = dict(zip(h, r))
        aid = str(r.get('activity_id') or '').strip()
        if not aid: skip['no activity id'] += 1; continue
        if aid in seen: skip['duplicate activity'] += 1; continue
        seen.add(aid)
        d = r['activity_date']
        try: d = d.date() if hasattr(d, 'date') else dt.date.fromisoformat(str(d)[:10])
        except ValueError: skip['unreadable date'] += 1; continue
        day = (d - start).days + 1
        typ = TYPES.get(str(r['activity_type'] or '').strip().lower())
        km = num(r['distance_km'])
        if not typ: skip[f"type {r['activity_type']}"] += 1; continue
        if not 1 <= day <= 10: skip['outside 1-10 Dec'] += 1; continue
        if not km or km <= 0: skip['zero distance'] += 1; continue
        if km > 250: skip['over 250 km (check)'] += 1; report.append(f"  check: {r['athlete_name']} {km} km on day {day}"); continue
        el, mv, ela = (r.get(k) for k in ('elevation_gain_m', 'moving_time_s', 'elapsed_time_s'))
        raw.append((str(r.get('athlete_id') or '').strip(), tidy(r['athlete_name']), day, round(km, 2), typ,
                    None if el in (None, '') else float(el), None if mv in (None, '') else int(mv),
                    None if ela in (None, '') else int(ela)))
    # one name per athlete_id: the most common spelling (a renamed Strava profile stays one person)
    names = defaultdict(Counter)
    for r in raw:
        if r[0]: names[r[0]][r[1]] += 1
    canon = {i: c.most_common(1)[0][0] for i, c in names.items()}
    for i, c in names.items():
        if len(c) > 1: report.append(f"  merged names for athlete {i}: {', '.join(c)} -> {canon[i]}")
    dupe = defaultdict(set)
    for i, n in canon.items(): dupe[n].add(i)
    for n, ids in dupe.items():   # different people with the same name stay separate: "Sam Lee", "Sam Lee (2)"
        if len(ids) > 1:
            for k, i in enumerate(sorted(ids)[1:], 2): canon[i] = f'{n} ({k})'
            report.append(f"  two Strava accounts share the name {n}: {sorted(ids)}; shown as {n}, {n} (2). Ask them to add an initial on Strava")
    acts = [[canon.get(r[0], r[1]), *r[2:]] for r in raw]
    if skip: report.append('skipped: ' + ', '.join(f'{v} {k}' for k, v in skip.most_common()))
    D = dict(base, acts=acts, year=year, start=start.isoformat(), parts=[], alltime={},
             window=f"{start:%A %-d} to {start + dt.timedelta(days=9):%A %-d %B}", note='')

# hand-kept side files
people = {a[0] for a in D['acts']}
flagged = set()
def check(name, where):
    if name and name not in people and name != 'Others' and (name, where) not in flagged:
        flagged.add((name, where)); report.append(f"  {where}: '{name}' has no activities yet (spelling? fine if they only pay)")
if A.src != '2025' or os.path.isdir(side):
    w = read('wagers.csv')
    if w or A.src != '2025':
        D['wagers'] = [{'no': r.get('no', str(i + 1)), 'wager': r.get('wager', ''), 'payer': tidy(r.get('payer')), 'amount': num(r.get('amount')) or 0} for i, r in enumerate(w)]
    pay = read('payments.csv')
    if pay or A.src != '2025':
        D['payments'] = {}
        for r in pay:
            n = tidy(r.get('name')); v = num(r.get('amount'))
            if n.lower().startswith('other') or n.lower().startswith('anon'): n = 'Others'
            if n and v: D['payments'][n] = D['payments'].get(n, 0) + v
    hs = read('hosts.csv')
    if hs: D['hosts'] = [{k: (v or 'TBC') if k in ('meeting_point', 'route', 'treats') else v for k, v in r.items()} for r in hs]
    D['crews'] = {tidy(r['name']): r['crew'] for r in read('crews.csv') if r.get('name') and r.get('crew')}
    att = defaultdict(list)
    for r in read('attendance.csv'):
        if r.get('day', '').isdigit() and r.get('name'): att[int(r['day'])].append(tidy(r['name']))
    D['attendance'] = {d: sorted(set(v)) for d, v in att.items()}
for w in D['wagers']: check(w['payer'], 'wager payer')
for n in D.get('payments', {}): check(n, 'payment')
for n in D.get('crews', {}): check(n, 'crew')
for d, v in D.get('attendance', {}).items():
    for n in v: check(n, f'attendance day {d}')

if A.src != '2025':
    through = A.through if A.through is not None else (today - start).days
    D['through'] = max(0, min(10, through))
    D['final'] = A.final
    if D['through'] == 0: sys.exit('No complete challenge day yet (Day 1 is complete from 2 December). Keep the preview page up; nothing written.')
    late = [a for a in D['acts'] if a[1] > D['through']]
    if late: report.append(f"  {len(late)} activities from day {D['through'] + 1}+ held back until that day is complete")
D['target'] = A.target
D.pop('runs', None)
from zoneinfo import ZoneInfo
D['updated'] = dt.datetime.now(ZoneInfo('Africa/Johannesburg')).strftime('%Y-%m-%dT%H:%M:%S')
json.dump(D, open(A.out, 'w'), separators=(',', ':'), ensure_ascii=False)
print(f"{A.out}: {len(D['acts'])} activities, {len({a[0] for a in D['acts']})} people, through day {D.get('through')}, final={D.get('final')}")
print('\n'.join(report) or 'nothing to flag')
