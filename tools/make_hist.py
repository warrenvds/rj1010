"""Pack the structured history CSVs (data/) into the compact JSON the page embeds."""
import csv, json, sys
d = sys.argv[1] if len(sys.argv) > 1 else 'data'
R = lambda f: list(csv.DictReader(open(f'{d}/{f}', encoding='utf-8')))
H = {
  'history': [{'year': int(h['year']), 'participants': int(h['participants']), 'runners': int(h['runners_logged']), 'finishers': int(h['finishers']), 'km': float(h['km']), 'top': h['top_runner'], 'funds': float(h['funds_raised']), 'final': h['funds_status'] == 'final'} for h in R('history.csv')],
  'runs': [[int(r['year']), r['athlete'], int(r['day']), round(float(r['km']), 2)] for r in R('runs.csv')],
  'awards': [{k: (int(v) if k == 'year' else v) for k, v in a.items()} for a in R('awards.csv')],
  'wagers': [{'year': int(w['year']), 'no': w['no'], 'wager': w['wager'], 'payer': w['payer'], 'amount': float(w['amount']) if w['amount'] else None} for w in R('wagers.csv')],
  'pets': [a['athlete'] for a in R('athletes.csv') if a['is_pet'] == 'yes'],
}
json.dump(H, open('tools/hist.json', 'w'), separators=(',', ':'), ensure_ascii=False)
print('hist.json', len(H['runs']), 'runs')
