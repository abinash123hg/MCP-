const $ = (id) => document.getElementById(id);
async function api(path, options={}) { const r=await fetch(path,{headers:{'Content-Type':'application/json'},...options}); const data=await r.json(); if(!r.ok) throw new Error(data.detail||'Request failed'); return data; }
function show(data){ $('snapshot').textContent=JSON.stringify(data,null,2); $('page-meta').textContent=`${data.title||""} — ${data.url||""}`; $('screenshot').src='/api/screenshot?t='+Date.now(); $('screenshot').style.display='block'; }
async function refresh(){ try{show(await api('/api/snapshot'));}catch(e){$('snapshot').textContent=e.message;} }
$('open').onclick=async()=>{try{show(await api('/api/open',{method:'POST',body:JSON.stringify({url:$('url').value})}));}catch(e){$('snapshot').textContent=e.message;}};
$('inspect').onclick=refresh; $('refresh').onclick=refresh;
$('click').onclick=async()=>{try{show(await api('/api/click',{method:'POST',body:JSON.stringify({selector:$('selector').value})}));}catch(e){$('snapshot').textContent=e.message;}};
$('fill').onclick=async()=>{try{show(await api('/api/fill',{method:'POST',body:JSON.stringify({selector:$('selector').value,value:$('value').value})}));}catch(e){$('snapshot').textContent=e.message;}};
$('ask').onclick=async()=>{try{const d=await api('/api/chat',{method:'POST',body:JSON.stringify({prompt:$('prompt').value})});$('answer').textContent=d.response;}catch(e){$('answer').textContent=e.message;}};
(async()=>{try{const d=await api('/api/health');$('health').textContent='● Online';$('health').title=d.mcp_endpoint+' • '+d.model+' • vision: '+d.vision_model;}catch(e){$('health').textContent='Offline';}})();
$('run-agent').onclick=async()=>{try{const d=await api('/api/agent',{method:'POST',body:JSON.stringify({goal:$('goal').value})});$('agent-result').textContent=JSON.stringify(d,null,2);if(d.results?.length){const last=d.results[d.results.length-1].result;if(last)show(last);}}catch(e){$('agent-result').textContent=e.message;}};
