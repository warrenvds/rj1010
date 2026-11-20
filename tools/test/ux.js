// Simulated first-time visitor: every tab, control, link and dialog, on phone and desktop, light and dark.
const { chromium, devices } = require('playwright'); const fs = require('fs');
const src = process.argv[2], tag = process.argv[3] || 'x', OUT = '/tmp/claude-0/ux/';
fs.mkdirSync(OUT, { recursive: true });
const d3src = fs.readFileSync('/home/claude/rj26/node_modules/d3/dist/d3.min.js', 'utf8');
fs.writeFileSync(OUT + tag + '.html', fs.readFileSync(src, 'utf8').replace(/<script src=[^>]+><\/script>/, () => '<script>' + d3src + '</script>'));
const URL0 = 'file://' + OUT + tag + '.html';
const issues = [], note = (...a) => issues.push(a.join(' '));
(async () => {
  const b = await chromium.launch();
  for (const [label, ctxOpt] of [['phone', { ...devices['iPhone 13'], colorScheme: 'light' }], ['desk', { viewport: { width: 1280, height: 900 }, colorScheme: 'dark' }]]) {
    const ctx = await b.newContext({ ...ctxOpt, acceptDownloads: true }); const p = await ctx.newPage();
    p.on('pageerror', e => note(label, 'JS error:', e.message));
    p.on('console', m => { if (m.type() === 'error' && !/fonts\.g|ERR_|net::/.test(m.text())) note(label, 'console:', m.text()); });
    const t0 = Date.now(); await p.goto(URL0 + '#current'); await p.waitForTimeout(500); console.log(label, 'load ms', Date.now() - t0);
    const tabs = await p.$$eval('nav.tabs a', as => as.map(a => a.dataset.tab));
    for (const tb of tabs) {
      await p.click(`nav.tabs a[data-tab="${tb}"]`); await p.waitForTimeout(350);
      const st = await p.evaluate(tb => ({ hash: location.hash, vis: !document.getElementById('p-' + tb).hidden, over: document.documentElement.scrollWidth - innerWidth,
        empty: [...document.querySelectorAll('#p-' + tb + ' table')].filter(t => t.offsetParent && !t.rows.length).map(t => t.id),
        unlabeled: [...document.querySelectorAll('#p-' + tb + ' button')].filter(x => x.offsetParent && !x.textContent.trim() && !x.getAttribute('aria-label')).length,
        h: document.body.scrollHeight }), tb);
      if (!st.vis) note(label, tb, 'page not shown'); if (st.over > 0) note(label, tb, 'horizontal overflow', st.over);
      if (st.empty.length) note(label, tb, 'empty tables', st.empty); if (st.unlabeled) note(label, tb, 'unlabeled buttons', st.unlabeled);
      await p.screenshot({ path: `${OUT}${tag}-${label}-${tb}.png`, fullPage: true });
    }
    // back button
    await p.goBack(); await p.waitForTimeout(200); const back = await p.evaluate(() => location.hash); console.log(label, 'after back:', back);
    if (await p.evaluate(() => [...document.querySelectorAll('section.page')].filter(s => !s.hidden).length) !== 1) note(label, 'back button leaves wrong page state');
    // current: search, sort, walk switch
    await p.goto(URL0 + '#current'); await p.waitForTimeout(300);
    const first = await p.$eval('#c-table tbody tr td.name .rn', e => e.textContent);
    await p.fill('#c-q', first.split(' ')[0]); await p.waitForTimeout(150); console.log(label, 'search', await p.textContent('#c-cnt'));
    await p.fill('#c-q', ''); await p.click('#c-table thead th:nth-child(2) button'); await p.click('#c-table thead th:nth-child(2) button');
    if (await p.isVisible('#walks')) { await p.click('#walks'); await p.waitForTimeout(200); console.log(label, 'walk switch', await p.textContent('#walks-lbl'), '|', await p.textContent('#walks-note')); await p.click('#walks'); } else console.log(label, 'walk switch hidden (no walks)');
    console.log(label, 'goals:', (await p.textContent('#g-note')).slice(0, 160)); console.log(label, 'records:', (await p.textContent('#r-note')).slice(0, 160));
    // profile + status picture
    await p.click(`#c-table [data-runner="${first}"]`); await p.waitForTimeout(300);
    if (!await p.evaluate(() => document.getElementById('runner').open)) note(label, 'profile did not open');
    const mk = await p.$('#r-body .r-share button');
    if (mk) { await mk.click(); await p.waitForSelector('#r-body .r-share img', { timeout: 5000 }).catch(() => note(label, 'status picture not made'));
      const src = await p.$eval('#r-body .r-share img', i => i.src).catch(() => null);
      if (src) { const buf = await p.evaluate(async s => { const r = await fetch(s); const a = new Uint8Array(await r.arrayBuffer()); let x = ''; for (const c of a) x += String.fromCharCode(c); return btoa(x); }, src); fs.writeFileSync(`${OUT}${tag}-status.png`, Buffer.from(buf, 'base64')); }
      const [dl] = await Promise.all([p.waitForEvent('download', { timeout: 3000 }).catch(() => null), p.click('#r-body .r-share a[download]')]); console.log(label, 'save image download:', dl && dl.suggestedFilename()); }
    else note(label, 'no status picture button for', first);
    await p.screenshot({ path: `${OUT}${tag}-${label}-profile.png` });
    await p.keyboard.press('Escape'); await p.waitForTimeout(150); if (await p.evaluate(() => document.getElementById('runner').open)) note(label, 'Escape did not close profile');
    // day by day: every day button + copy
    await p.goto(URL0 + '#days'); await p.waitForTimeout(300);
    for (const btn of await p.$$('#daypick button')) { await btn.click(); await p.waitForTimeout(60); }
    console.log(label, 'recap last lines:', (await p.inputValue('#recap')).split('\n').slice(-6).join(' / '));
    // hosts: calendar
    await p.goto(URL0 + '#hosts'); await p.waitForTimeout(300);
    const nh = await p.$$eval('#h-list .host', h => h.length); if (nh !== 10) note(label, 'hosted runs: expected 10 cards, found', nh);
    const [all] = await Promise.all([p.waitForEvent('download', { timeout: 3000 }).catch(() => null), p.click('#h-all')]);
    if (all) { const ics = fs.readFileSync(await all.path(), 'utf8'); console.log(label, 'ics events', (ics.match(/BEGIN:VEVENT/g) || []).length, 'lines >75 chars', ics.split('\r\n').filter(l => l.length > 75).length); } else note(label, 'all-runs calendar download failed');
    // past: every year, name click, sort
    await p.goto(URL0 + '#past'); await p.waitForTimeout(300);
    for (const y of await p.$$eval('#yearpick button', bs => bs.map(x => x.textContent))) { await p.click(`#yearpick button:has-text("${y}")`); await p.waitForTimeout(120); const n = await p.$$eval('#y-table tbody tr', r => r.length); if (!n) note(label, 'past', y, 'empty leaderboard'); }
    // links audit
    const links = await p.$$eval('a[href]', as => as.map(a => ({ h: a.getAttribute('href'), t: a.textContent.trim().slice(0, 40), blank: a.target === '_blank', rel: a.rel })));
    const pages = await p.$$eval('section.page', s => s.map(x => x.id.slice(2)));
    for (const l of links) {
      if (l.h.startsWith('#')) { const k = l.h.slice(1).split('-')[0]; if (!pages.includes(k)) note(label, 'internal link to missing page', l.h, l.t); }
      else if (/^https?:/.test(l.h)) { if (!l.blank) note(label, 'external link opens in same tab', l.h); if (!/noopener/.test(l.rel)) note(label, 'external link without noopener', l.h); }
      else if (!/^blob:|^data:/.test(l.h)) note(label, 'odd link', l.h);
    }
    console.log(label, 'links checked', links.length, 'external:', [...new Set(links.filter(l => /^http/.test(l.h)).map(l => l.h.split('?')[0]))].join(' '));
    await ctx.close();
  }
  await b.close();
  console.log('ISSUES', issues.length ? '\n- ' + [...new Set(issues)].join('\n- ') : 'none');
})();
