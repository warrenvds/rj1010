# RJ 10/10 Challenge dashboard

Public dashboard for the Retro Joes Athletics Club 10/10 Challenge (1 to 10 December), raising money for the Ruth First and Theo Jackson funds.

The page is a single self-contained `index.html`, rebuilt each day from the Strava export and published with GitHub Pages.

## Daily refresh (07:00, 2 to 12 December)

Kobus drops the day's export (`Activities` sheet, same columns, walks and hikes included) in the Drive folder by about 06:30. Then:

```
python3 tools/build_data.py export.xlsx 2026-12-01 /tmp/d.json      # through = yesterday, worked out from today's date
python3 tools/make_site.py /tmp/d.json index.html
```

`build_data.py` prints what it skipped (wrong type, outside 1 to 10 Dec, duplicates, zero or impossible distances) and any names in the side files it can't match. Read that before pushing.

Add `--final` from 07:00 on Saturday 12 December. Before 2 December it refuses to build, so the preview stays up.

## Hand-kept files: `data/2026/`

| File | Columns | From |
|---|---|---|
| `wagers.csv` | no, wager, payer, amount | Warren forwards wagers as they're made |
| `payments.csv` | name, amount, date, note | Warren forwards who paid; one row per payment, repeats add up. Use `Others` for donations not linked to a runner |
| `crews.csv` | name, crew | Runners who team up; everyone else is in a surname crew |
| `attendance.csv` | day, name | Hosts' lists of who came to each hosted run |

Names must match the Strava name. Words typed in capitals are tidied automatically.

## Tests

`tools/test/gen.py` makes a fake 120-runner challenge export with the usual problems in it. `verify.py` recomputes the totals straight from the export; `tpage.js` checks the built page against them and against JavaScript errors.
