"""Build the dashboard data from a Strava export xlsx (the dev's format) or the 2025 replay.
Usage: python3 build_data.py <xlsx|2025> <start YYYY-MM-DD> <out.json>"""
import sys, json, datetime as dt
src, start, out = sys.argv[1], dt.date.fromisoformat(sys.argv[2]), sys.argv[3]
base = json.load(open('tools/data2025.json'))
TYPES = {'run': 'Run', 'trail run': 'Trail Run', 'treadmill': 'Treadmill', 'treadmill workout': 'Treadmill',
         'virtual run': 'Treadmill', 'walk': 'Walk', 'hike': 'Walk'}
if src == '2025':
    acts = [[a, d, k, 'Run', None, None, None] for a, d, k in base['runs']]
    D = dict(base, acts=acts, year=2025, start='2026-12-01', window='Tuesday 1 to Thursday 10 December',
             note='Preview: these are the 2025 results replayed so you can see how the 2026 page will work. Hosts are confirmed; meeting points, crews and the target are still to come.')
else:
    import openpyxl
    ws = openpyxl.load_workbook(src, data_only=True)['Activities']
    rows = list(ws.iter_rows(values_only=True)); h = rows[0]
    seen, acts, skipped = set(), [], []
    for r in rows[1:]:
        r = dict(zip(h, r))
        if not r['activity_id'] or r['activity_id'] in seen: continue
        seen.add(r['activity_id'])
        d = r['activity_date']; d = d.date() if hasattr(d, 'date') else dt.date.fromisoformat(str(d)[:10])
        day = (d - start).days + 1
        typ = TYPES.get(str(r['activity_type']).strip().lower())
        if not (1 <= day <= 10) or not typ: skipped.append((r['athlete_name'], str(d), r['activity_type'])); continue
        el = r['elevation_gain_m']; mv = r['moving_time_s']
        acts.append([r['athlete_name'].strip(), day, round(float(r['distance_km'] or 0), 2), typ,
                     None if el in (None, '') else float(el), None if mv in (None, '') else int(mv),
                     None if r['elapsed_time_s'] in (None, '') else int(r['elapsed_time_s'])])
    end = start + dt.timedelta(days=9)
    D = dict(base, acts=acts, year=start.year, start=start.isoformat(), parts=[], wagers=[], alltime={},
             window=f"Pipeline test: {start:%-d %b} to {end:%-d %b %Y}",
             note=f"Pipeline test: {len(acts)} activities from {len({a[0] for a in acts})} runners, read from the Strava export in Google Drive, with {start:%-d %b} treated as Day 1. Not real challenge results.")
    print('skipped outside window/type:', len(skipped))
D.pop('runs', None)
D['updated'] = dt.date.today().isoformat()
json.dump(D, open(out, 'w'), separators=(',', ':'), ensure_ascii=False)
print(out, len(D['acts']), 'activities')
