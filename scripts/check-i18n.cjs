// Behaviour checks for language navigation and the one-time verification flow.
// No real verification code or network request is used.
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const assert=require('node:assert/strict');
const root=path.join(__dirname,'..');
const language=fs.readFileSync(path.join(root,'language.js'),'utf8');
function navigation(url){
  const handlers={};
  const links=['/privacy.html','/en/privacy.html'].map(href=>({href,getAttribute:()=>href}));
  const location=new URL(url);
  vm.runInNewContext(language,{URL,URLSearchParams,location,document:{querySelectorAll:()=>links},window:{addEventListener:(event,fn)=>handlers[event]=fn}});
  return {links,handlers,location};
}
let n=navigation('https://lexote.com.tr/privacy.html?k=linkedin&oobCode=private-value#section');
assert.equal(n.links[1].href,'/en/privacy.html?k=linkedin#section');
assert(!n.links[1].href.includes('private-value'));
// Browser link.href returns an absolute URL after assignment.
n.links.forEach(link=>link.href=new URL(link.href,n.location).href);
n.location.hash='#contact';n.handlers.hashchange();
assert.equal(n.links[1].href,'/en/privacy.html?k=linkedin#contact');
n=navigation('https://lexote.com.tr/privacy.html?k=bad%20tag');
assert.equal(n.links[1].href,'/en/privacy.html');

const page=fs.readFileSync(path.join(root,'dogrula.html'),'utf8');
const scripts=[...page.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
async function verification(pathname,query){
  let fetches=0,replaced=null,historyPath=null;
  const elements={};
  const element=id=>elements[id]||(elements[id]={hidden:true,className:'',textContent:'',setAttribute(k,v){this[k]=v},addEventListener(k,v){this[k]=v}});
  const buttons=['tr','en'].map(lang=>({lang,setAttribute(k,v){this[k]=v},getAttribute:()=>lang,addEventListener(k,v){this[k]=v}}));
  const context={URLSearchParams,encodeURIComponent,window:{},location:{pathname,search:query,replace:p=>replaced=p},history:{replaceState:(_a,_b,p)=>historyPath=p},document:{documentElement:{lang:'tr'},getElementById:element,querySelectorAll:()=>buttons},fetch:()=>{fetches++;return Promise.resolve({ok:true})}};
  vm.createContext(context);
  for(const s of scripts)vm.runInContext(s,context);
  await new Promise(resolve=>setImmediate(resolve));
  return {context,elements,buttons,get fetches(){return fetches},replaced,historyPath};
}
(async()=>{
  const query='?mode=verifyEmail&oobCode='+('x'.repeat(25))+'&apiKey='+('y'.repeat(25));
  let v=await verification('/dogrula.html',query);
  assert.equal(v.fetches,1);
  assert.equal(v.historyPath,'/dogrula.html');
  assert.equal(v.elements.title.textContent,'E-posta adresiniz doğrulandı');
  v.buttons[1].click();
  assert.equal(v.context.document.documentElement.lang,'en');
  assert.equal(v.elements.title.textContent,'Your email address has been verified');
  assert.equal(v.elements.open.textContent,'Open Lexote');
  assert.equal(v.fetches,1,'Changing language must not reuse the one-time code');
  v.buttons[0].click();assert.equal(v.fetches,1);
  v=await verification('/en/dogrula.html',query);
  assert.equal(v.context.document.documentElement.lang,'en');
  v=await verification('/en/dogrula.html',query+'&lang=tr');
  assert.equal(v.context.document.documentElement.lang,'tr');
  v=await verification('/en/dogrula.html','?mode=bad');
  assert.equal(v.fetches,0);assert.equal(v.replaced,'/en/');
  for(const name of ['index.html','privacy.html','terms.html','dogrula.html','404.html'])for(const prefix of ['', 'en/']){
    const html=fs.readFileSync(path.join(root,prefix+name),'utf8');
    for(const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){
      if(match[1].includes('application/ld+json'))JSON.parse(match[2]);
      else if(!match[1].includes('src='))new vm.Script(match[2],{filename:prefix+name});
    }
  }
  console.log('PASS: campaign/hash preservation, private query exclusion, language switching without re-verification, verification locale/redirects, all inline JS and JSON-LD syntax.');
})().catch(e=>{console.error(e);process.exitCode=1});
