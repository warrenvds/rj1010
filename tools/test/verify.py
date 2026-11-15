"""Recompute the numbers straight from the export, without build_data.py's code."""
import sys, json, openpyxl, datetime as dt
from collections import defaultdict
xlsx, js, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
D = json.load(open(js))
ws = openpyxl.load_workbook(xlsx)['Activities']; rows = list(ws.iter_rows(values_only=True)); h = rows[0]
ok = {'run', 'trail run', 'walk', 'treadmill', 'hike', 'virtual run', 'treadmill workout'}
seen, by_id = set(), defaultdict(float)
for r in rows[1:]:
    r = dict(zip(h, r))
    if r['activity_id'] in seen: continue
    seen.add(r['activity_id'])
    day = (r['activity_date'].date() - dt.date(2026, 12, 1)).days + 1
    if str(r['activity_type']).lower() in ok and 1 <= day <= N and 0 < (r['distance_km'] or 0) <= 250: by_id[r['athlete_id']] += round(r['distance_km'], 2)
page = defaultdict(float)
for a in D['acts']:
    if a[1] <= N: page[a[0]] += a[2]
x = sorted(round(v, 2) for v in by_id.values()); y = sorted(round(v, 2) for v in page.values())
print(f'people {len(x)} vs {len(y)}; km {sum(x):.2f} vs {sum(y):.2f}; per-person totals match: {x == y}')
fin = sum(v >= 100 for v in page.values()); r2 = sum(2 * max(0, 100 - v) for v in page.values()) if N == 10 else 0
wag = sum(w['amount'] for w in D['wagers']); pay = sum(D['payments'].values())
exp = {'km': sum(y), 'runners': len(y), 'fin': fin, 'r2': r2, 'wag': wag, 'pledged': sum(int(k + 0.5) for k in page.values()) + sum(int(2 * max(0, 100 - k) + 0.5) for k in page.values() if N == 10) + wag + sum(0 for w in D['wagers']), 'received': pay,
       'N': N, 'onpace': sum(v >= 10 * N for v in page.values())}
json.dump(exp, open(js + '.exp', 'w')); print({k: round(v, 2) for k, v in exp.items()})
