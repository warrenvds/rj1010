# RJ 10/10 Challenge data, 2018 to 2025

Every edition of the Retro Joes 10/10 Challenge in one consistent format, taken from the club's RJ 10/10 workbook. Each file is plain CSV with a header row, so it opens in Excel or Google Sheets and loads straight into code.

New years are added in the same format: one row per runner per day in `runs.csv`, plus that year's row in `history.csv`.

## Files

### history.csv — one row per edition
| Column | Meaning |
|---|---|
| year | Edition year (the challenge runs 1 to 10 December) |
| participants | Entrants as recorded in the workbook's History sheet, including people who only donated or bet |
| runners_logged | People with at least one km in `runs.csv` |
| finishers | Runners reaching 100 km, from the History sheet |
| km | Club total km, from the History sheet |
| top_runner | Most km that year |
| funds_raised | Rand raised for the Ruth First and Theo Jackson funds |
| funds_status | `final`, or `to be confirmed` while payments are still coming in |

### runs.csv — one row per runner per day with a run
| Column | Meaning |
|---|---|
| year | Edition year |
| athlete | Runner's name as used across years |
| day | 1 to 10 for 1 to 10 December. **0 means a total for the whole challenge**: 2018 only has totals per runner |
| km | Distance, 2 decimals |
| pace | Average pace min:sec per km, where captured (2020 onward) |
| elevation_m | Elevation gain in metres, where captured (2020 onward) |

Days with no run are left out rather than stored as 0.

### awards.csv — the awards as they were announced
| Column | Meaning |
|---|---|
| year, award | Edition and award name, e.g. The Goat |
| winner | Winner as announced |
| value | The winning figure, e.g. 3175m or 04:10 |
| second, third | Podium places, where the award had one |
| description | What the award was for |

2018 had no awards recorded in the workbook. Committee awards (The Mampara, The Flamboyant, The Creep) are kept as announced.

### wagers.csv — the wager book
| Column | Meaning |
|---|---|
| year, no | Edition and wager number |
| wager | The wager as written in the group |
| payer | Who pays |
| amount | Rand the wager came to. Blank for 2021 and 2022, where only the wording survives |

The standing R1 per km and R2 per km-short contributions aren't listed as wagers. No wager lists survive for 2018 to 2020.

### athletes.csv — one row per person across all years
| Column | Meaning |
|---|---|
| athlete | Name |
| is_pet | `yes` for the club's four-legged runners |
| editions | How many 10/10s they've logged km in |
| first_year, last_year | First and most recent edition |
| total_km | All-time km in the 10/10 |
| best_year, best_km | Their biggest year |
| finishes_100km | Editions where they reached 100 km |

## Notes on the source
- 2018 comes from the year's results table, which has totals only.
- 2019 comes from the year's daily results sheet; 2020 to 2025 come from the daily input sheets.
- Totals reconcile with the History sheet to within rounding: 2018 differs by 2 km because its totals were whole numbers.
- Finisher counts in `history.csv` are as recorded. Counting from `runs.csv` gives 7 for 2018, 14 for 2019 and 35 for 2025.
- Payments and amounts paid by individuals are deliberately not in this public dataset.
