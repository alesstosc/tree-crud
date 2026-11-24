#!/usr/bin/env python3
"""Tree CRUD — python3 tree-crud.py  ->  http://localhost:8080"""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

PORT = 8080

HTML = r"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tree CRUD</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:#f8f9fa;height:100vh;height:100dvh;display:flex;flex-direction:column;overflow:hidden;-webkit-text-size-adjust:100%}
header{background:#1a1a2e;color:#fff;padding:10px 20px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;row-gap:6px;flex:0 0 auto}
header .brand{font-weight:700;margin-right:16px;white-space:nowrap}
header button{background:#16213e;color:#fff;border:1px solid #0f3460;padding:6px 14px;border-radius:4px;cursor:pointer;font-size:13px;min-height:34px;white-space:nowrap}
header button:hover{background:#0f3460}
header .sep{width:1px;height:22px;background:#333;margin:0 6px}
header .fill{flex:1 1 0}
.main{display:flex;flex:1;overflow:hidden;min-height:0}
.left{flex:0 0 auto;width:380px;max-width:100%;overflow:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;background:#fff;padding:12px}
.right{flex:1 1 0;min-width:0;padding:20px;overflow:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;background:#f8f9fa}
.gutter{flex:0 0 14px;width:14px;position:relative;cursor:col-resize;touch-action:none;background:#eceff3;border-left:1px solid #dde1e6;border-right:1px solid #dde1e6;display:flex;align-items:center;justify-content:center;user-select:none;-webkit-user-select:none;outline:none}
.gutter::before{content:"";width:3px;height:40px;border-radius:3px;background:#c6ccd4;transition:background .15s,height .15s}
.gutter:hover::before,.gutter:focus-visible::before,.gutter.active::before{background:#2d7ff9;height:56px}
.gutter:hover,.gutter.active{background:#e5eefb}
body.split-drag{cursor:col-resize;user-select:none;-webkit-user-select:none;touch-action:none}
@media (max-width:760px){
 header{padding:8px 10px;gap:6px}
 header .brand{font-size:15px;margin-right:6px}
 header button{padding:6px 10px;font-size:12.5px}
 header .sep{display:none}
 .left{padding:8px}
 .right{padding:12px}
 .fg input,.fg textarea{font-size:16px}
 ul.tree li>.item{padding:8px;font-size:15px}
 ul.tree ul{padding-left:16px}
 .gutter{flex:0 0 16px;width:16px}
 .gutter::before{height:52px}
 #msg{font-size:11px;white-space:normal}
}
@media (hover:none){
 header button:hover{background:#16213e}
 ul.tree li>.item:hover{background:transparent}
 .gutter:hover,.gutter.active{background:#eceff3}
 .gutter:hover::before{background:#c6ccd4;height:40px}
 .gutter.active,.gutter.active:hover{background:#e5eefb}
 .gutter.active::before,.gutter.active:hover::before{background:#2d7ff9;height:56px}
}
.fg{margin-bottom:14px}
.fg label{display:block;font-size:12px;font-weight:600;color:#555;margin-bottom:4px;text-transform:uppercase}
.fg input,.fg textarea{width:100%;padding:8px 10px;border:1px solid #ddd;border-radius:4px;font-size:14px}
.fg textarea{min-height:120px;resize:vertical}
.fg .note-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}
.fg .note-head label{margin-bottom:0}
.fg .note-head button{font-size:11px;padding:2px 10px;border:1px solid #ccc;border-radius:4px;background:#f3f3f3;cursor:pointer}
.fg .notes-render{width:100%;padding:8px 10px;border:1px solid #ddd;border-radius:4px;font-size:14px;min-height:120px;max-height:320px;overflow:auto;white-space:pre-wrap;background:#fff;word-break:break-word}
.fg .notes-render:empty:before{content:attr(data-placeholder);color:#999;pointer-events:none}
.fg input:focus,.fg textarea:focus{border-color:#1a1a2e;outline:none}
ul.tree{list-style:none;padding-left:0}
ul.tree ul{list-style:none;padding-left:22px}
ul.tree li{padding:3px 0}
ul.tree li>.item{display:flex;align-items:center;gap:6px;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:14px}
ul.tree li>.item:hover{background:#f0f0f0}
ul.tree li>.item.sel{background:#e3f2fd;font-weight:600}
ul.tree li>.item .toggle{width:16px;text-align:center;font-size:10px;color:#888;cursor:pointer;flex-shrink:0}
ul.tree li>.item .label{flex:1}
ul.tree li>.item .badge{font-size:10px;color:#999}
input[type=file]{display:none}
#msg{font-size:12px;color:#888;margin-left:auto}
</style>
</head>
<body>
<header>
<span class="brand">Tree CRUD</span>
<button onclick="addChild()">+ Figlio</button>
<button onclick="addSibling()">+ Fratello</button>
<button onclick="delNode()">Elimina</button>
<span class="sep"></span>
<button onclick="newTree()">Nuovo</button>
<button onclick="loadFile()">Carica JSON</button>
<input type="file" id="fin" accept=".json" onchange="importFile(event)">
<span class="sep"></span>
<button onclick="exportJSON()">Export JSON</button>
<button onclick="exportMD()">Export MD</button>
<button onclick="iaRulesOpen()">Regole Tree</button>
<button onclick="iaOpen()">IA</button>
<button onclick="infoOpen()">Info</button>
<span class="fill"></span>
<span id="msg"></span>
</header>
<div class="main" id="main">
<div class="left" id="tree"></div>
<div class="gutter" id="gutter" role="separator" aria-orientation="vertical" aria-label="Ridimensiona i pannelli" tabindex="0" title="Trascina (o usa le frecce) per spostare il divisorio"></div>
<div class="right" id="panel">
<div class="fg">
<label>Nome nodo</label>
<input id="ename" oninput="onEdit()" placeholder="Nome...">
</div>
<div class="fg">
<div class="note-head">
<label>Note</label>
<button type="button" id="enotes-toggle" onclick="noteToggle()">Testo</button>
</div>
<textarea id="enotes" oninput="onEdit()" placeholder="Dettagli, requisiti..." rows="8" hidden></textarea>
<div id="enotes-view" class="notes-render" data-placeholder="Dettagli, requisiti..."></div>
</div>
<div style="font-size:12px;color:#999" id="epath"></div>
</div>
</div>
<script>
var D=[], cur=null, nid=1, jn="";
var LS="treecrud";
var TOUCH_ONLY=false;
try{TOUCH_ONLY=!!(window.matchMedia&&window.matchMedia("(hover:none) and (pointer:coarse)").matches)}catch(e){}

function load(){
 var s=localStorage.getItem(LS);
 if(s){try{
  var d=JSON.parse(s);
  var san=iaSanitizeTree(d,{next:1});
  if(san && san.length>0){D=san;nid=1+maxId(D);save();render();return}
 }catch(e){}}
 initDefault();save();render()
}
function save(){localStorage.setItem(LS,JSON.stringify(D))}

function initDefault(){
 nid=1;D=[{id:nid++,t:"Nuovo Progetto",n:"",c:[]}]
}

function maxId(a){var m=0;for(var i=0;i<a.length;i++){if(a[i].id>m)m=a[i].id;if(a[i].c)m=Math.max(m,maxId(a[i].c))}return m}

function render(){
 var e=document.getElementById("tree");
 e.innerHTML=html(D);
 var ts=e.querySelectorAll(".toggle");
 for(var i=0;i<ts.length;i++){var u=ts[i].parentElement.nextElementSibling;if(u&&u.tagName=="UL"){u.style.display="block";ts[i].textContent="\u25be"}}
 if(cur){var it=e.querySelector('[data-id="'+cur+'"]');if(it)it.classList.add("sel")}
 showForm()
}

function html(a){
 var h='<ul class="tree">';
 for(var i=0;i<a.length;i++){
  var x=a[i], hk=x.c&&x.c.length>0;
  var id=parseInt(x.id,10); if(!isFinite(id)) id=0;
  h+='<li><div class="item" draggable="'+(TOUCH_ONLY?"false":"true")+'" data-id="'+id+'" onclick="sel('+id+')">';
  h+='<span class="toggle" onclick="event.stopPropagation();tgl(this)">'+(hk?"\u25be":"")+'</span>';
  h+='<span class="label">'+esc(x.t)+'</span>';
  if(hk)h+='<span class="badge">'+cnt(x)+'</span>';
  h+='</div>';
  if(hk)h+='<ul>'+html(x.c)+'</ul>';
  h+='</li>'
 }
 return h+'</ul>'
}
function cnt(x){var c=0;if(x.c)for(var i=0;i<x.c.length;i++)c+=1+cnt(x.c[i]);return c}
function tgl(e){var u=e.parentElement.nextElementSibling;if(u&&u.tagName=="UL"){u.style.display=u.style.display=="none"?"block":"none";e.textContent=u.style.display=="none"?"\u25b8":"\u25be"}}
function esc(s){return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}
function sel(id){cur=id;render()}
function find(a,id){for(var i=0;i<a.length;i++){if(a[i].id==id)return a[i];if(a[i].c){var f=find(a[i].c,id);if(f)return f}}return null}
function parentOf(a,id,p){for(var i=0;i<a.length;i++){if(a[i].id==id)return p;if(a[i].c){var f=parentOf(a[i].c,id,a[i]);if(f)return f}}return null}

var NOTE_MODE="view";
function noteToggle(){
 NOTE_MODE=NOTE_MODE==="text"?"view":"text";
 var ta=document.getElementById("enotes"),vw=document.getElementById("enotes-view"),bt=document.getElementById("enotes-toggle");
 if(NOTE_MODE==="view"){
  var nd=cur!=null?find(D,cur):null;
  vw.innerHTML=nd?nd.n||"":"";
  ta.hidden=true;vw.hidden=false;bt.textContent="Testo";
 }else{
  ta.hidden=false;vw.hidden=true;bt.textContent="Grafico";
  ta.focus();
 }
}

function showForm(){
 var n=document.getElementById("ename"),no=document.getElementById("enotes"),vw=document.getElementById("enotes-view"),p=document.getElementById("epath");
 if(!cur){n.value="";no.value="";vw.innerHTML="";p.textContent="Seleziona un nodo";n.disabled=true;no.disabled=true;return}
 var nd=find(D,cur);if(!nd){cur=null;showForm();return}
 n.disabled=false;no.disabled=false;
 if(document.activeElement!==n)n.value=nd.t||"";
 if(document.activeElement!==no)no.value=nd.n||"";
 vw.innerHTML=nd.n||"";
 p.textContent="Percorso: "+path(cur)
}
function path(id){
 function w(a,t){for(var i=0;i<a.length;i++){if(a[i].id==t)return[a[i].t];if(a[i].c){var p=w(a[i].c,t);if(p)return[a[i].t].concat(p)}}return null}
 var p=w(D,id);return p?p.join(" / "):""
}
function onEdit(){
 if(!cur)return;var nd=find(D,cur);if(!nd)return;
 nd.t=document.getElementById("ename").value;
 nd.n=document.getElementById("enotes").value;
 save();render()
}
function addChild(){
 if(!cur){alert("Seleziona un nodo.");return}
 var p=find(D,cur);if(!p)return;
 iaPropose("child",p,null)
}
function addSibling(){
 if(!cur){alert("Seleziona un nodo.");return}
 var p=parentOf(D,cur,null);if(!p){alert("La radice non ha fratelli.");return}
 var ref=find(D,cur);
 iaPropose("sibling",p,ref)
}
function delNode(){
 if(!cur){alert("Seleziona un nodo.");return}
 var nd=find(D,cur);
 if(cur==D[0].id){alert("Non puoi eliminare la radice.");return}
 if(!confirm("Eliminare "+nd.t+" e figli?"))return;
 var p=parentOf(D,cur,null);
 if(p)p.c=p.c.filter(function(c){return c.id!=cur});else D=D.filter(function(c){return c.id!=cur})
 cur=null;save();render()
}
function newTree(){
 if(!confirm("Creare nuovo albero vuoto?"))return;
 nid=1;jn="";D=[{id:nid++,t:"Nuovo progetto",n:"",c:[]}];cur=null;save();render();
 msg("Nuovo albero creato")
}
function loadFile(){document.getElementById("fin").click()}
function iaSanitizeTree(a, counter){
  var out = [];
  if (!Array.isArray(a)) { return out; }
  for (var i = 0; i < a.length; i++) {
    var node = a[i];
    if (!node || typeof node !== "object") { continue; }
    var clean = { id: counter.next++, t: String(node.t == null ? "" : node.t), n: String(node.n == null ? "" : node.n), c: [] };
    clean.c = iaSanitizeTree(node.c, counter);
    out.push(clean);
  }
  return out;
}
function importFile(e){
 var f=e.target.files[0]; if(!f){ e.target.value=""; return; }
 var r=new FileReader();
 r.onload=function(ev){
  try{
   var d=JSON.parse(ev.target.result);
   var sanitized=iaSanitizeTree(d,{next:1});
   if(Array.isArray(sanitized) && sanitized.length>0){
    D=sanitized; nid=1+maxId(D); jn=f.name.replace(/\.json$/i,""); save(); cur=null; render(); msg("Caricato: "+f.name);
   } else { alert("JSON non valido"); }
  }catch(err){ alert("Errore: "+err.message); }
 };
 r.readAsText(f); e.target.value="";
}
function exportJSON(){
 var nm=prompt("Nome file:",jn||"progetto");if(!nm)return;
 jn=nm;
 var b=new Blob([JSON.stringify(D,null,2)],{type:"application/json"});
 var u=URL.createObjectURL(b),a=document.createElement("a");
 a.href=u;a.download=nm+".json";a.click();URL.revokeObjectURL(u);
 msg("JSON esportato: "+nm+".json")
}

function mdText(s){
 return String(s==null?"":s).replace(/\r?\n/g," ").replace(/[ \t]+/g," ").trim();
}
function mdBullet(node, level){
 var ind="  ".repeat(level);
 var out=ind+"- "+mdText(node.t)+"\n";
 var note=String(node.n==null?"":node.n).trim();
 if(note)out+=ind+"  "+note.replace(/\r?\n/g,"\n"+ind+"  ")+"\n";
 for(var i=0;(node.c||[]).length>i;i++)out+=mdBullet(node.c[i], level+1);
 return out;
}
function mdNodes(list, depth){
 var out="";
 for(var i=0;(list||[]).length>i;i++){
  var node=list[i];
  if(depth<6){
   out+="\n"+"#".repeat(depth+1)+" "+mdText(node.t)+"\n\n";
   var note=String(node.n==null?"":node.n).trim();
   if(note)out+=note+"\n\n";
   out+=mdNodes(node.c||[], depth+1);
  }else{
   out+=mdBullet(node, 0)+"\n";
  }
 }
 return out;
}
function exportMD(){
 var nm=prompt("Nome file:",jn||"progetto");if(!nm)return;
 jn=nm;
 var md=mdNodes(D,0);
 md=md.replace(/\n{3,}/g,"\n\n").trim()+"\n";
 var b=new Blob([md],{type:"text/markdown;charset=utf-8"});
 var u=URL.createObjectURL(b),a=document.createElement("a");
 a.href=u;a.download=nm+".md";a.click();URL.revokeObjectURL(u);
 msg("Markdown esportato: "+nm+".md")
}

function cntAll(a){var c=0;for(var i=0;i<a.length;i++){c+=1;if(a[i].c)c+=cntAll(a[i].c)}return c}
function msg(s){var e=document.getElementById("msg");e.textContent=s;setTimeout(function(){e.textContent=""},3000)}

load();

/* --- divisorio trascinabile (albero | note) --- */
var SPLIT_KEY="treecrud_split", SPLIT_MIN=140, SPLIT_MIN_RIGHT=150, splitWant=380;
function splitClamp(w){
 var main=document.getElementById("main");
 var total=(main&&main.clientWidth)||window.innerWidth||0;
 var max=Math.max(SPLIT_MIN, total-SPLIT_MIN_RIGHT);
 w=parseInt(w,10); if(!isFinite(w)) w=SPLIT_MIN;
 return Math.max(SPLIT_MIN, Math.min(Math.round(w), max));
}
function splitSet(w, persist){
 var left=document.getElementById("tree");
 if(!left){return}
 splitWant=w;
 var v=splitClamp(w);
 left.style.width=v+"px";
 if(persist){try{localStorage.setItem(SPLIT_KEY,String(v))}catch(e){}}
}
function splitInit(){
 var saved=null;
 try{var s=localStorage.getItem(SPLIT_KEY); if(s)saved=parseInt(s,10)}catch(e){}
 var def=(window.innerWidth<760)?Math.round(window.innerWidth*0.46):380;
 splitSet((saved&&saved>0)?saved:def,false);
}
function splitDragInit(){
 var g=document.getElementById("gutter");
 if(!g){return}
 var dragging=false, startX=0, startW=0, pid=null;
 function down(e){
  if(e.pointerType==="mouse" && e.button!==0){return}
  dragging=true; startX=e.clientX; startW=document.getElementById("tree").getBoundingClientRect().width;
  g.classList.add("active"); document.body.classList.add("split-drag"); pid=e.pointerId;
  try{if(g.setPointerCapture&&pid!=null)g.setPointerCapture(pid)}catch(err){}
  e.preventDefault();
 }
 function move(e){
  if(!dragging){return}
  splitSet(startW+(e.clientX-startX),false);
  e.preventDefault();
 }
 function up(e){
  if(!dragging){return}
  dragging=false; g.classList.remove("active"); document.body.classList.remove("split-drag");
  try{if(g.releasePointerCapture&&pid!=null)g.releasePointerCapture(pid)}catch(err){}
  splitSet(splitWant,true); pid=null;
 }
 if(window.PointerEvent){
  g.addEventListener("pointerdown",down);
  g.addEventListener("pointermove",move);
  g.addEventListener("pointerup",up);
  g.addEventListener("pointercancel",up);
 }else{
  g.addEventListener("mousedown",function(e){
   if(e.button!==0){return}
   dragging=true; startX=e.clientX; startW=document.getElementById("tree").getBoundingClientRect().width;
   g.classList.add("active"); document.body.classList.add("split-drag"); e.preventDefault();
  });
  document.addEventListener("mousemove",function(e){if(dragging){splitSet(startW+(e.clientX-startX),false)}});
  document.addEventListener("mouseup",function(){
   if(!dragging){return}
   dragging=false; g.classList.remove("active"); document.body.classList.remove("split-drag"); splitSet(splitWant,true);
  });
 }
 g.addEventListener("dblclick",function(){splitSet((window.innerWidth<760)?Math.round(window.innerWidth*0.46):380,true)});
 g.addEventListener("keydown",function(e){
  var step=e.shiftKey?40:12;
  if(e.key==="ArrowLeft"||e.key==="Left"){splitSet(splitWant-step,true);e.preventDefault()}
  else if(e.key==="ArrowRight"||e.key==="Right"){splitSet(splitWant+step,true);e.preventDefault()}
  else if(e.key==="Home"){splitSet(SPLIT_MIN,true);e.preventDefault()}
  else if(e.key==="End"){splitSet(1e6,true);e.preventDefault()}
 });
 window.addEventListener("resize",function(){splitSet(splitWant,false)});
 window.addEventListener("orientationchange",function(){splitSet(splitWant,false)});
 splitInit();
}
if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",splitDragInit)}else{splitDragInit()}

var IA_KEYSTORE = "treecrud_deepseek_key";
var IA_MODELSTORE = "treecrud_deepseek_model";
var IA_ENDPOINT = "https://api.deepseek.com/chat/completions";
var IA_MIN = 3;
var IA_PENDING = null;
var IA_CHOICES = [];
function iaKey(){
  var v = "";
  try { v = localStorage.getItem(IA_KEYSTORE) || sessionStorage.getItem(IA_KEYSTORE) || ""; } catch(e) {}
  return v;
}
function iaModel(){
  var v = "";
  try { v = localStorage.getItem(IA_MODELSTORE) || ""; } catch(e) {}
  return v || "deepseek-chat";
}
function iaOpen(){
  document.getElementById("ia").style.display = "flex";
  iaLoadConfig();
}
function iaClose(){
  document.getElementById("ia").style.display = "none";
}
function iaLoadConfig(){
  var k = "", m = "", remember = true;
  try {
    m = localStorage.getItem(IA_MODELSTORE) || "";
    k = localStorage.getItem(IA_KEYSTORE) || "";
    if (k) { remember = true; }
    else { k = sessionStorage.getItem(IA_KEYSTORE) || ""; remember = !k; }
  } catch(e) {}
  var rem = document.getElementById("ia-remember");
  if (rem) { rem.checked = remember; }
  document.getElementById("ia-key").value = k;
  document.getElementById("ia-model").value = m || "deepseek-chat";
  document.getElementById("ia-status").textContent = k ? "Configurato." : "Inserisci la API key DeepSeek.";
}
function iaSaveConfig(){
  var key = document.getElementById("ia-key").value.trim();
  var rem = document.getElementById("ia-remember");
  var remember = rem ? rem.checked : true;
  try {
    localStorage.setItem(IA_MODELSTORE, document.getElementById("ia-model").value);
    if (remember) {
      if (key) { localStorage.setItem(IA_KEYSTORE, key); } else { localStorage.removeItem(IA_KEYSTORE); }
      sessionStorage.removeItem(IA_KEYSTORE);
    } else {
      if (key) { sessionStorage.setItem(IA_KEYSTORE, key); } else { sessionStorage.removeItem(IA_KEYSTORE); }
      localStorage.removeItem(IA_KEYSTORE);
    }
  } catch(e) {}
  document.getElementById("ia-status").textContent = key ? (remember ? "Chiave salvata su questo browser." : "Chiave tenuta solo per questa sessione.") : "Inserisci la API key.";
}
function iaChooserOpen(title, status){
  document.getElementById("ia-chooser-title").textContent = title;
  document.getElementById("ia-chooser-body").innerHTML = "";
  document.getElementById("ia-custom").value = "";
  document.getElementById("ia-chooser-status").textContent = status || "";
  document.getElementById("ia-chooser").style.display = "flex";
}
function iaChooserStatus(t){
  document.getElementById("ia-chooser-status").textContent = t || "";
}
function iaChooserClose(){
  document.getElementById("ia-chooser").style.display = "none";
  IA_PENDING = null;
  IA_CHOICES = [];
}
function iaAppendNode(parent, name, note){
  if (!parent) { parent = D[0]; }
  if (!parent) { return null; }
  if (!parent.c) { parent.c = []; }
  var node = { id: nid++, t: name, n: note || "", c: [] };
  parent.c.push(node);
  return node;
}
function iaAddOne(parent, name, note){
  var node = iaAppendNode(parent, name, note);
  if (!node) { return; }
  save();
  render();
  sel(node.id);
  msg("Nodo aggiunto: " + node.t);
}
function iaPromptFallback(mode, parent){
  var na = prompt(mode === "sibling" ? "Nome nuovo fratello:" : "Nome nuovo figlio:");
  if (!na) { return; }
  iaAddOne(parent, na, "");
}
function iaRenderChoices(list){
  IA_CHOICES = list;
  var body = document.getElementById("ia-chooser-body");
  body.innerHTML = "";
  for (var i = 0; i < list.length; i++) {
    var s = list[i];
    var item = document.createElement("label");
    item.className = "ia-item";
    var chk = document.createElement("input");
    chk.type = "checkbox";
    chk.setAttribute("data-idx", String(i));
    var content = document.createElement("div");
    content.className = "ia-content";
    var title = document.createElement("span");
    title.className = "ia-title";
    title.innerHTML = s.titolo || "(senza titolo)";
    var notes = document.createElement("span");
    notes.className = "ia-notes";
    notes.innerHTML = s.note || "";
    content.appendChild(title);
    content.appendChild(notes);
    item.appendChild(chk);
    item.appendChild(content);
    body.appendChild(item);
  }
}
function iaChooserAccept(){
  if (!IA_PENDING) { return; }
  var boxes = document.getElementById("ia-chooser-body").querySelectorAll("input[type=checkbox]");
  var last = null;
  var count = 0;
  for (var i = 0; i < boxes.length; i++) {
    if (boxes[i].checked) {
      var s = IA_CHOICES[parseInt(boxes[i].getAttribute("data-idx"), 10)];
      if (s) { last = iaAppendNode(IA_PENDING.parent, s.titolo || "Nuovo ramo", s.note || ""); count++; }
    }
  }
  var custom = document.getElementById("ia-custom").value.trim();
  if (custom) { last = iaAppendNode(IA_PENDING.parent, custom, ""); count++; }
  if (!count) { iaChooserStatus("Seleziona almeno un suggerimento."); return; }
  save();
  render();
  if (last) { sel(last.id); }
  msg("Aggiunti " + count + " nodi");
  iaChooserClose();
}



function iaNorm(s){
  return String(s || "").trim().toLowerCase();
}
function iaPropose(mode, parent, ref){
  var key = iaKey();
  if (!key) { iaPromptFallback(mode, parent); return; }
  var title = mode === "sibling" ? "Possibili fratelli" : "Possibili figli";
  iaChooserOpen(title, "Interrogo " + iaModel() + "...");
  IA_PENDING = { mode: mode, parent: parent };
  var existing = (parent.c || []).map(function(n){ return n.t; });
  var regole = iaRulesGet().trim();
  var rel;
  var formato;
  if (mode === "sibling") {
    formato = JSON.stringify({ categoria: "...", suggerimenti: [{ titolo: "...", note: "..." }] });
    rel = "Contesto: il nodo padre e \"" + parent.t + "\"; i fratelli gia presenti allo stesso livello sono: " + JSON.stringify(existing) + ". Devi proporre nuovi FRATELLI con lo STESSO livello di astrazione e la STESSA categoria tassonomica dei fratelli esistenti. Passo 1: individua la categoria comune dei fratelli esistenti (es. epoche storiche, moduli, pagine, capitoli, sezioni) e scrivila nel campo 'categoria'. Passo 2: proponi SOLO altri elementi mancanti di quella identica categoria. Esempio: se i fratelli sono 'Preistoria', 'Medioevo', 'Evo Contemporaneo', i nuovi suggerimenti devono essere altre epoche (es. 'Evo Antico', 'Evo Moderno'), MAI sotto-argomenti, processi o temi di dettaglio come 'Metallurgia e reti di scambio'. Non riproporre ne duplicare i nomi esistenti. Ogni suggerimento deve essere omogeneo per tipo e granularita con i fratelli esistenti.";
  } else {
    formato = JSON.stringify({ suggerimenti: [{ titolo: "...", note: "..." }] });
    rel = "Proponi almeno 5 possibili FIGLI del nodo \"" + parent.t + "\", coerenti con le note e con granularita uniforme tra loro.";
  }
  var sys = "Sei un architetto software ed esperto di tassonomie. Ricevi un albero di progetto in JSON con nodi {id,t,n,c} (id numerico, t titolo, n note, c figli). " + rel + " Rispondi SOLO con JSON valido nel formato " + formato + ". Fornisci almeno 3 suggerimenti validi (meglio 5), titoli brevi e note tecniche concise." + (regole ? " REGOLE DEL PROGETTO da rispettare rigorosamente: " + regole : "");
  var isChat = iaModel() === "deepseek-chat";
  var payload = {
    model: iaModel(),
    messages: [
      { role: "system", content: sys },
      { role: "user", content: "Albero del progetto (JSON):\n" + JSON.stringify(D) }
    ]
  };
  if (isChat) {
    payload.temperature = mode === "sibling" ? 0.4 : 0.8;
    payload.response_format = { type: "json_object" };
  }
  fetch(IA_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Authorization": "Bearer " + key },
    body: JSON.stringify(payload)
  }).then(function(r){
    return r.text().then(function(t){
      if (!r.ok) { throw new Error("HTTP " + r.status + ": " + t.slice(0, 200)); }
      return t;
    });
  }).then(function(txt){
    var data = JSON.parse(txt);
    var content = data && data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content;
    if (!content) { throw new Error("Risposta vuota dal modello"); }
    var parsed = JSON.parse(String(content).trim().replace(/^```json/i, "").replace(/```$/, ""));
    var list = parsed.suggerimenti || [];
    if (mode === "sibling") {
      var seen = {};
      for (var e = 0; e < existing.length; e++) { seen[iaNorm(existing[e])] = true; }
      var kept = [];
      for (var i = 0; i < list.length; i++) {
        var k = iaNorm(list[i] && list[i].titolo);
        if (!k || seen[k]) { continue; }
        seen[k] = true;
        kept.push(list[i]);
      }
      list = kept;
    }
    if (list.length < IA_MIN) { throw new Error("Suggerimenti unici insufficienti (" + list.length + ")"); }
    var label = (mode === "sibling" && parsed.categoria) ? ("Categoria: " + parsed.categoria + ". ") : "";
    iaChooserStatus(label + "Scegli uno o piu suggerimenti.");
    iaRenderChoices(list);
  }).catch(function(e){
    msg("Errore IA: " + e.message);
    iaChooserClose();
    iaPromptFallback(mode, parent);
  });
}


var IA_DRAG_ID = null;
function iaItemOf(el){
  while (el && !(el.classList && el.classList.contains("item"))) { el = el.parentElement; }
  return el;
}
function iaParentArray(a, id){
  for (var i = 0; i < a.length; i++) {
    if (a[i].id == id) { return a; }
    if (a[i].c) { var r = iaParentArray(a[i].c, id); if (r) { return r; } }
  }
  return null;
}
function iaDndClear(){
  var els = document.querySelectorAll(".drop-before, .drop-after");
  for (var i = 0; i < els.length; i++) { els[i].classList.remove("drop-before"); els[i].classList.remove("drop-after"); els[i].removeAttribute("data-drop"); }
}
function iaDndMove(srcId, tgtId, after){
  if (srcId == tgtId) { return; }
  var arr = iaParentArray(D, srcId);
  if (!arr || iaParentArray(D, tgtId) !== arr) { return; }
  var si = -1;
  for (var i = 0; i < arr.length; i++) { if (arr[i].id == srcId) { si = i; break; } }
  if (si < 0) { return; }
  var node = arr.splice(si, 1)[0];
  var ti = -1;
  for (var j = 0; j < arr.length; j++) { if (arr[j].id == tgtId) { ti = j; break; } }
  if (ti < 0) { arr.splice(si, 0, node); return; }
  arr.splice(after ? ti + 1 : ti, 0, node);
  save();
  render();
}
function iaDndInit(){
  var tree = document.getElementById("tree");
  if (!tree || tree.getAttribute("data-dnd") === "1") { return; }
  tree.setAttribute("data-dnd", "1");
  tree.addEventListener("dragstart", function(e){
    var it = iaItemOf(e.target);
    if (!it) { return; }
    IA_DRAG_ID = parseInt(it.getAttribute("data-id"), 10);
    it.classList.add("dragging");
    try { e.dataTransfer.effectAllowed = "move"; e.dataTransfer.setData("text/plain", String(IA_DRAG_ID)); } catch(err) {}
  });
  tree.addEventListener("dragend", function(e){
    var it = iaItemOf(e.target);
    if (it) { it.classList.remove("dragging"); }
    iaDndClear();
    IA_DRAG_ID = null;
  });
  tree.addEventListener("dragover", function(e){
    var it = iaItemOf(e.target);
    if (!it || IA_DRAG_ID === null) { return; }
    var targetId = parseInt(it.getAttribute("data-id"), 10);
    if (targetId === IA_DRAG_ID) { return; }
    var srcArr = iaParentArray(D, IA_DRAG_ID);
    var ok = srcArr && iaParentArray(D, targetId) === srcArr;
    iaDndClear();
    if (!ok) { e.dataTransfer.dropEffect = "none"; return; }
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    var rect = it.getBoundingClientRect();
    var after = (e.clientY - rect.top) > (rect.height / 2);
    it.classList.add(after ? "drop-after" : "drop-before");
    it.setAttribute("data-drop", after ? "after" : "before");
  });
  tree.addEventListener("drop", function(e){
    var it = iaItemOf(e.target);
    if (!it || IA_DRAG_ID === null) { iaDndClear(); IA_DRAG_ID = null; return; }
    e.preventDefault();
    var targetId = parseInt(it.getAttribute("data-id"), 10);
    var after = it.getAttribute("data-drop") === "after";
    iaDndMove(IA_DRAG_ID, targetId, after);
    iaDndClear();
    IA_DRAG_ID = null;
  });
}
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", iaDndInit);
} else {
  iaDndInit();
}


var IA_RULESSTORE = "treecrud_ia_rules";
var IA_RULES_DEFAULT = "Le proposte della IA devono rispettare queste regole.\n1. Livello tassonomico: ogni ramo proposto deve stare allo stesso livello di astrazione del nodo di riferimento.\n2. Fratelli: stessa categoria dei fratelli esistenti; se formano una sequenza (es. epoche storiche) proponi gli elementi mancanti di quella sequenza, mai sotto-argomenti o temi di dettaglio.\n3. Figli: granularita uniforme e coerente con le note del nodo padre.\n4. Non duplicare nodi gia presenti allo stesso livello.\n5. Titoli brevi, note tecniche concise.\n6. Mantieni coerenza con il tronco e con il resto dell'albero.";
function iaRulesGet(){
  var v = "";
  try { v = localStorage.getItem(IA_RULESSTORE) || ""; } catch(e) {}
  return v || IA_RULES_DEFAULT;
}
function iaRulesOpen(){
  document.getElementById("ia-rules-text").value = iaRulesGet();
  document.getElementById("ia-rules-status").textContent = "";
  document.getElementById("ia-rules").style.display = "flex";
}
function iaRulesClose(){
  document.getElementById("ia-rules").style.display = "none";
}
function iaRulesSave(){
  var v = document.getElementById("ia-rules-text").value.trim();
  try {
    if (v && v !== IA_RULES_DEFAULT) { localStorage.setItem(IA_RULESSTORE, v); }
    else { localStorage.removeItem(IA_RULESSTORE); }
  } catch(e) {}
  document.getElementById("ia-rules-status").textContent = (v && v !== IA_RULES_DEFAULT) ? "Regole salvate." : "Regole default attive.";
  msg("Regole Tree aggiornate");
}
function iaRulesReset(){
  document.getElementById("ia-rules-text").value = IA_RULES_DEFAULT;
  try { localStorage.removeItem(IA_RULESSTORE); } catch(e) {}
  document.getElementById("ia-rules-status").textContent = "Regole default ripristinate.";
}
function infoOpen(){
  document.getElementById("info").style.display = "flex";
}
function infoClose(){
  document.getElementById("info").style.display = "none";
}

</script>

<style>
.ia-wrap{position:fixed;inset:0;background:rgba(0,0,0,.45);display:none;align-items:center;justify-content:center;z-index:999;padding:10px}
.ia-box{background:#fff;color:#222;width:min(720px,94vw);max-height:88vh;max-height:88dvh;overflow:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;border-radius:12px;padding:18px;box-shadow:0 20px 60px rgba(0,0,0,.35)}
@media (max-width:760px){.ia-box{width:100%;max-width:none;padding:14px;border-radius:10px;max-height:92vh;max-height:92dvh}.ia-row input,.ia-row select{min-width:0}.ia-actions{flex-wrap:wrap}}
.ia-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.ia-row{display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap}
.ia-row input,.ia-row select{flex:1;min-width:200px;padding:6px 8px;border:1px solid #ccc;border-radius:6px}
.ia-actions{display:flex;gap:10px;align-items:center;margin-bottom:8px}
.ia-box button{padding:6px 10px;border:1px solid #ccc;border-radius:6px;background:#f3f3f3;cursor:pointer}
.ia-item{display:flex;align-items:flex-start;gap:10px;border:1px solid #e3e3e3;border-radius:8px;padding:10px;margin-bottom:10px;background:#fafafa;cursor:pointer}
.ia-item>input{flex:0 0 auto;margin:3px 0 0 0}
.ia-content{flex:1;min-width:0}
.ia-title{display:block;font-weight:600;margin-bottom:4px}
.ia-notes{display:block;font-size:13px;color:#444;white-space:pre-wrap}
.ia-hint{font-size:12px;color:#999}
.item[draggable="true"]{cursor:grab}
.item.dragging{opacity:.45}
.item.drop-before{box-shadow:inset 0 3px 0 0 #2d7ff9}
.item.drop-after{box-shadow:inset 0 -3px 0 0 #2d7ff9}
.info-body h3{font-size:14px;margin:14px 0 4px;color:#1a1a2e}
.info-body p{font-size:13px;line-height:1.55;color:#444;margin:0 0 8px}
.info-body code{background:#f3f3f3;padding:1px 5px;border-radius:4px;font-size:12px}
.info-body .warn{background:#fff8e1;border:1px solid #ffe082;border-radius:8px;padding:10px 12px}
.ia-row textarea{flex:1;width:100%;min-height:220px;padding:8px;border:1px solid #ccc;border-radius:6px;font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;resize:vertical}
</style>
<div id="ia" class="ia-wrap">
  <div class="ia-box">
    <div class="ia-head">
      <strong>Configurazione IA (DeepSeek)</strong>
      <button onclick="iaClose()">Chiudi</button>
    </div>
    <div class="ia-row">
      <label>API key</label>
      <input id="ia-key" type="password" placeholder="sk-..." oninput="iaSaveConfig()">
    </div>
    <div class="ia-row">
      <label style="display:flex;gap:8px;align-items:center">
        <input id="ia-remember" type="checkbox" checked onchange="iaSaveConfig()" style="flex:0 0 auto;min-width:0;width:16px;height:16px;padding:0">
        Ricorda la chiave su questo browser
      </label>
    </div>
    <div class="ia-hint">La chiave resta nel browser e non viene inviata al server. Non usarla su PC condivisi.</div>
    <div class="ia-row">
      <label>Modello</label>
      <select id="ia-model" onchange="iaSaveConfig()">
        <option value="deepseek-chat">deepseek-chat</option>
        <option value="deepseek-reasoner">deepseek-reasoner</option>
      </select>
    </div>
    <div class="ia-actions"><span id="ia-status" class="ia-hint"></span></div>
  </div>
</div>
<div id="ia-chooser" class="ia-wrap">
  <div class="ia-box">
    <div class="ia-head">
      <strong id="ia-chooser-title">Suggerimenti IA</strong>
      <button onclick="iaChooserClose()">Annulla</button>
    </div>
    <div id="ia-chooser-body"></div>
    <div class="ia-row">
      <label>Oppure nome personalizzato</label>
      <input id="ia-custom" placeholder="Nome...">
    </div>
    <div class="ia-actions">
      <button onclick="iaChooserAccept()">Aggiungi selezionati</button>
      <span id="ia-chooser-status" class="ia-hint"></span>
    </div>
  </div>
</div>


<div id="ia-rules" class="ia-wrap">
  <div class="ia-box">
    <div class="ia-head">
      <strong>Regole Tree (istruzioni per la IA)</strong>
      <button onclick="iaRulesClose()">Chiudi</button>
    </div>
    <div class="ia-row" style="align-items:stretch">
      <textarea id="ia-rules-text" spellcheck="false"></textarea>
    </div>
    <div class="ia-actions">
      <button onclick="iaRulesSave()">Salva regole</button>
      <button onclick="iaRulesReset()">Ripristina default</button>
      <span id="ia-rules-status" class="ia-hint"></span>
    </div>
  </div>
</div>

<div id="info" class="ia-wrap">
  <div class="ia-box">
    <div class="ia-head">
      <strong>Tree CRUD — panoramica</strong>
      <button onclick="infoClose()">Chiudi</button>
    </div>
    <div class="info-body">
      <h3>Cosa fa Tree CRUD</h3>
      <p>App single-file per creare e organizzare alberi gerarchici: progetti, tassonomie, piani, indici. Ogni nodo ha un titolo e delle note; puoi aggiungere figli e fratelli, riordinare i rami con il drag & drop, importare ed esportare JSON. Il salvataggio è automatico nel browser (localStorage): non servono server né database, basta <code>python3 tree-crud.py</code> e aprire http://localhost:8080.</p>
      <h3>IA e DeepSeek</h3>
      <div class="warn"><p style="margin:0"><b>Per renderla realmente operativa serve una API key DeepSeek.</b> I pulsanti «+ Figlio» e «+ Fratello» chiedono all'IA suggerimenti per estendere l'albero, coerenti con le «Regole Tree». Crea la key gratuitamente su <b>platform.deepseek.com</b> (sezione API Keys) e inseriscila nel pannello «IA».</p></div>
      <p>Senza key l'app resta comunque pienamente utilizzabile in modalità manuale: i nuovi nodi verranno chiesti con una semplice richiesta di testo.</p>
      <h3>Layout e mobile</h3>
      <p>Il divisorio tra l'albero e il pannello titolo/note è <b>trascinabile</b> (mouse o dito): trascinalo per allargare l'uno o l'altro. La posizione viene ricordata dal browser; <b>doppio click</b> (o <b>doppio tap</b>) riporta la misura di default, e da tastiera si usa <code>Tab</code> + frecce. Su schermi piccoli il divisorio parte al centro, il menu si dispone su più righe e i campi usano caratteri da 16px per evitare lo zoom automatico di iOS.</p>
      <h3>Privacy</h3>
      <p>La key resta nel tuo browser (localStorage, o solo per la sessione, a tua scelta) e viene inviata esclusivamente all'endpoint DeepSeek. Non passa mai dal server locale e non viene mai scritta sul disco del progetto.</p>
    </div>
  </div>
</div>

</body>
</html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        b = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, f, *a): pass

if __name__ == "__main__":
    print(f"\n  Tree CRUD  ->  http://localhost:{PORT}/\n")
    ThreadingHTTPServer(("localhost", PORT), H).serve_forever()
