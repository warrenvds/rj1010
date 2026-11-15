"""Synthetic RJ 10/10 export in Kobus's format with deliberate problems."""
import random, csv, datetime as dt, openpyxl
random.seed(7)
first = "Anna Ben Carla Dev Erin Femi Gina Hugo Ivy Jono Kate Lwazi Mia Nandi Omar Pia Quinn Ravi Sipho Tess Uma Vusi Wes Xoli Yusuf Zara Lebo Thabo Kim Rory".split()
last = "Naidoo Botha Smith Dlamini Pillay Jacobs van Wyk Mokoena du Plessis Khumalo Adams Nel Petersen Morais Whelan".split()
people = []
ids = 1000
while len(people) < 118:
    n = f"{random.choice(first)} {random.choice(last)}"
    if n in [p[1] for p in people]: continue
    ids += 1; people.append((str(ids), n))
people.append(('9001', 'Sam Lee')); people.append(('9002', 'Sam Lee'))   # two different people, same name
start = dt.date(2026, 12, 1)
rows, aid = [], 50_000
def add(pid, name, d, typ, km, el=None, mv=None):
    global aid; aid += 1
    mv = mv if mv is not None else int(km * random.uniform(300, 480))
    rows.append([name, dt.datetime.combine(d, dt.time(5, 30)), typ, round(km, 2), (int(mv * random.uniform(1, 1.3)) if mv != "" else ""), mv, el, km / (mv / 3600) if mv else None,
                 None, None, f"RJ 10/10 Challenge - Day {(d - start).days + 1}", str(aid), pid, '', '', ''])
for pid, name in people:
    keen = random.random()
    for day in range(-3, 14):
        d = start + dt.timedelta(days=day - 1)
        if random.random() > (0.5 + keen / 2): continue
        typ = random.choices(['Run', 'Trail Run', 'Walk', 'Treadmill', 'Hike', 'Ride', 'Swim', 'Workout'], [60, 8, 15, 5, 3, 5, 2, 2])[0]
        km = max(0.3, random.gauss(10 if typ != 'Walk' else 5, 4))
        add(pid, name, d, typ, km, el=None if random.random() < 0.1 else round(km * random.uniform(2, 25)))
        if random.random() < 0.15: add(pid, name, d, 'Run', random.uniform(2, 6))   # second activity same day
# deliberate problems
rows.append(list(rows[10]))                                  # exact duplicate row (same activity_id)
rows.append(list(rows[20]))
pid, name = people[0]; add(pid, name.upper(), start + dt.timedelta(days=2), 'Run', 8)      # ALL CAPS name, same id
pid, name = people[1]; add(pid, name.split()[0] + ' ' + name.split()[1] + '-Renamed', start + dt.timedelta(days=4), 'Run', 7)  # renamed profile mid-challenge
add(people[2][0], people[2][1], start + dt.timedelta(days=3), 'Run', 0)                    # zero distance
add(people[3][0], people[3][1], start + dt.timedelta(days=5), 'Run', 412)                  # GPS glitch
add(people[4][0], people[4][1], start + dt.timedelta(days=6), 'Run', 9, el='', mv='')      # blank optional fields
add('9500', 'lowercase person', start + dt.timedelta(days=1), 'Run', 11)                   # lower case name
late = [r for r in rows if r[1].date() == start + dt.timedelta(days=9)][:6]                # 6 day-10 runs uploaded late
for r in late: rows.remove(r)
H = ['athlete_name','activity_date','activity_type','distance_km','elapsed_time_s','moving_time_s','elevation_gain_m','avg_speed_kmh','elapsed_time','moving_time','activity_name','activity_id','athlete_id','activity_url','profile_url','data_notes']
def save(f, rr):
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = 'Activities'; ws.append(H)
    for r in rr: ws.append(r)
    wb.create_sheet('Definitions'); wb.save(f)
def upto(day):   # what the export looks like on the morning of 1 Dec + day (includes the partial current day)
    cut = start + dt.timedelta(days=day)
    return [r for r in rows if r[1].date() <= cut]
for day in (1, 5, 10): save(f'export_day{day}.xlsx', upto(day))
save('export_final.xlsx', rows + late)
random.shuffle(people)
names = [p[1] for p in people]
with open('side/wagers.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['no', 'wager', 'payer', 'amount'])
    for i, n in enumerate(names[:25]): w.writerow([i + 1, f'{n} pays R{(i % 5 + 1) * 100} if beaten by a sibling', n, (i % 5 + 1) * 100])
    w.writerow([26, 'Mystery wager', 'Not A Runner', 250])
with open('side/payments.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['name', 'amount', 'date'])
    for n in names[:40]: w.writerow([n, random.choice([50, 100, 150, 200]), '2026-12-12'])
    w.writerow([names[0], 'R1,000', '2026-12-13']); w.writerow(['Others', 500, '2026-12-14']); w.writerow([names[1].upper(), 75, '2026-12-14'])
with open('side/crews.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['name', 'crew'])
    for n in names[5:9]: w.writerow([n, 'Crew Dawn Patrol'])
with open('side/attendance.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['day', 'name'])
    for d in range(1, 11):
        for n in random.sample(names[:30], 8): w.writerow([d, n])
    w.writerow([3, names[0]])   # listed twice on one day
print(len(rows) + len(late), 'rows;', len(people), 'people')
