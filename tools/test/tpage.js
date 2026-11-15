const {JSDOM,VirtualConsole}=require('jsdom');const fs=require('fs');
const [file,expf]=process.argv.slice(2); const exp=JSON.parse(fs.readFileSync(expf));
let html=fs.readFileSync(file,'utf8').replace(/<script src=[^>]+><\/script>/,'').replace(/<link[^>]+>/g,'');
const errs=[]; const vc=new VirtualConsole(); vc.on('jsdomError',e=>errs.push(e.message)); vc.on('error',e=>errs.push(String(e)));
const dom=new JSDOM(html,{runScripts:'outside-only',url:'https://x/#current',virtualConsole:vc});
const w=dom.window; w.d3=require('d3'); w.matchMedia=()=>({addEventListener(){}}); w.requestAnimationFrame=f=>f();
w.addEventListener('error',e=>errs.push(e.message));
const s=html.slice(html.lastIndexOf('<script>')+8,html.lastIndexOf('</script>'));
try{w.eval(s);}catch(e){errs.push('load: '+e.stack.split('\n').slice(0,2).join(' '))}
const d=w.document, $=id=>d.getElementById(id), T=id=>($(id)||{}).textContent;
const tabs=['days','awards','hosts','money','past','past-2019','past-2018','past-2024','current'];
for(const h of tabs){try{w.location.hash=h;w.eval('show()');}catch(e){errs.push(h+': '+e.message)}}

const R=v=>+String(v).replace(/[^\d.-]/g,'');
const rows=[...d.querySelectorAll('#m-owe tbody tr')].map(r=>[...r.cells].map(c=>c.textContent));
const due=rows.reduce((a,r)=>a+R(r[5]),0), paid=rows.reduce((a,r)=>a+R(r[6]||0),0);
const stats=T('m-stats');
const check=(name,got,want)=>console.log((Math.abs(got-want)<1.01?'  ok ':'  XX ')+name+': page '+got+' / expected '+(+want.toFixed(2)));
console.log(file,'|',T('c-title'),'|',T('c-lead'));
check('owed total (sum of table)',due,exp.pledged); check('paid total (sum of table)',paid,exp.received);
check('pledged headline',R(T('m-pledged')),exp.pledged);
check('received stat',R(stats.match(/R[\d,]+(?=received)/)[0]),exp.received);
check('people in current table',d.querySelectorAll('#c-table tbody tr').length,exp.runners);
const lead=T('c-lead'); check('km in lead',R(lead.match(/([\d,]+\.\d) km/)[1]),exp.km); check(exp.N===10?'reached 100 in lead':'on track in lead',R(lead.match(/(\d+) (are on track|reached)/)[1]),exp.N===10?exp.fin:exp.onpace);
console.log('  status mix:',JSON.stringify(rows.reduce((a,r)=>(a[r[7]]=(a[r[7]]||0)+1,a),{})),'| rows',rows.length);
console.log('  groupies:',[...d.querySelectorAll('#a-classic .award')].filter(e=>/Groupies/.test(e.textContent)).map(e=>e.textContent).join(''));
console.log('  crews:',T('c-crews').slice(0,140));
console.log('  recap tail:',$('recap').value.split('\n').slice(-4).join(' / '));
console.log('  sam lee rows:',[...d.querySelectorAll('#c-table tbody tr')].filter(r=>/Sam Lee/.test(r.textContent)).length, '| errors:',errs.length?errs:'none');
