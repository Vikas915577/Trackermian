from pathlib import Path
import re

ROOT=Path('.')


def replace_once(s, old, new, label):
    n=s.count(old)
    if n != 1:
        raise RuntimeError(f'{label}: expected 1 match, got {n}')
    return s.replace(old,new,1)

app_path=ROOT/'app.js'
if not app_path.exists():
    raise SystemExit('app.js not found. Run this from the repository root.')
s=app_path.read_text(encoding='utf-8')

# Version
s=s.replace("const VERSION='V24.1';", "const VERSION='V24.2';", 1)

# Community state
if 'let v24CommunityStats=' not in s:
    s=replace_once(s, "  let v24AccessToken='';", "  let v24AccessToken='';\n  let v24CommunityStats={state:'idle',total_users:0,public_users:0,active_now:0,active_24h:0};", 'community state')

# Creator top card
if 'function v24CreatorTopCard()' not in s:
    helper="""  function v24CreatorTopCard(){
    const n=creatorName()||'Vashu Sharmaa',h=creatorHandle()||'@pandatvikas1';
    return '<section class="v24-creator-top"><div class="v24-creator-top-head"><img class="v24-creator-main" src="creator-profile.jpg" alt="'+escapeHtml(n)+'" loading="eager"><div class="v24-creator-copy"><span class="kicker">CREDIT BY</span><b>'+escapeHtml(n)+'</b><small>Data Engineer · '+escapeHtml(h)+'</small></div><button class="btn v24-creator-view" data-v20-nav="more" data-v20-more="creator">View</button></div><div class="v24-creator-gallery" aria-label="Creator photos"><img src="creator-photo-1.jpg" alt="'+escapeHtml(n)+'" loading="lazy"><img src="creator-photo-2.jpg" alt="'+escapeHtml(n)+'" loading="lazy"><img src="creator-photo-3.jpg" alt="'+escapeHtml(n)+'" loading="lazy"></div></section>';
  }
"""
    pos=s.find('  function v24CreatorCompact(){')
    if pos<0: raise RuntimeError('creator compact helper not found')
    s=s[:pos]+helper+s[pos:]

# Today: creator at top, not duplicated at bottom
start=s.rfind('  function v20Today(){')
end=s.find('\n  function v24Week()', start)
if start<0 or end<0: raise RuntimeError('final v20Today not found')
part=s[start:end]
part=part.replace('<div class="v24-page">','<div class="v24-page">${v24CreatorTopCard()}',1)
part=part.replace('${v24CreatorCompact()}','',1)
s=s[:start]+part+s[end:]

# New-user/login creator card
if 'function v24LoginCreator()' not in s:
    lh="""function v24LoginCreator(){return '<section class="v24-login-creator"><div class="kicker">CREDIT BY</div><div class="v24-login-creator-head"><img src="creator-profile.jpg" alt="Vashu Sharmaa"><div><b>Vashu Sharmaa</b><small>Data Engineer · @pandatvikas1</small></div></div><div class="v24-login-gallery"><img src="creator-photo-1.jpg" alt="Vashu Sharmaa"><img src="creator-photo-2.jpg" alt="Vashu Sharmaa"><img src="creator-photo-3.jpg" alt="Vashu Sharmaa"></div></section>';}
"""
    pos=s.rfind('function profileLogin(){')
    end=s.find('\n\nfunction resetProfile(){',pos)
    if pos<0 or end<0: raise RuntimeError('profileLogin not found')
    login=s[pos:end]
    login=replace_once(login,'<div class="login-card">','<div class="login-card">${v24LoginCreator()}','login creator')
    s=s[:pos]+lh+login+s[end:]

# Rank RPC helper
if 'async function rankFetch(name,args)' not in s:
    marker='  // Exact Top 20 RPC + exact own rank. No Instagram is returned to the player UI.'
    helper="""  async function rankFetch(name,args){
    if(!cloudReady())throw new Error('Backend not configured');
    const r=await fetch(CLOUD_CFG.url+'/rest/v1/rpc/'+encodeURIComponent(name),{method:'POST',headers:{apikey:CLOUD_CFG.anonKey,Authorization:'Bearer '+(v24AccessToken||CLOUD_CFG.anonKey),'Content-Type':'application/json'},body:JSON.stringify(args||{})});
    if(!r.ok)throw new Error(name+' '+r.status);
    return await r.json();
  }

"""
    s=replace_once(s,marker,helper+marker,'rank helper')

# Final rank loader
ls=s.rfind('  v20LoadRank=async function(){')
le=s.find('  // Keep the score helper aligned',ls)
if ls<0 or le<0: raise RuntimeError('final rank loader not found')
loader="""  v20LoadRank=async function(){
    if(v20RankStatus==='loading')return;
    v20RankStatus='loading';v20RankError='';v24RankMyGlobal=null;v24CommunityStats={state:'loading',total_users:0,public_users:0,active_now:0,active_24h:0};renderV20();
    if(!cloudReady()){v20RankStatus='offline';v20RankError='Community backend is not configured.';v20RankRows=[];v20RankActive=[];v24CommunityStats={state:'offline',total_users:0,public_users:0,active_now:0,active_24h:0};renderV20();return;}
    try{
      if(data.cloudOptIn)await cloudSync({silent:true});
      const rows=await rankFetch('get_public_leaderboard',{p_limit:20});
      v20RankRows=(Array.isArray(rows)?rows:[]).map((x,i)=>Object.assign({},x,{rankScore:Number(x.rank_score)||0,__rank:Number(x.rank)||i+1}));
      if(data.cloudOptIn&&data.publicProfile){try{const session=await v24CloudSession();const rr=await rankFetch('get_public_rank',{p_user_id:session.user.id});if(Array.isArray(rr)&&rr[0])v24RankMyGlobal=Object.assign({},rr[0],{rank:Number(rr[0].rank)||null});}catch(e){}}
      try{const ar=await rankFetch('get_public_active_members',{p_minutes:15,p_limit:6});v20RankActive=Array.isArray(ar)?ar:[];}catch(e){v20RankActive=[];}
      try{const cr=await rankFetch('get_community_stats',{});if(Array.isArray(cr)&&cr[0])v24CommunityStats={state:'ready',total_users:Number(cr[0].total_users)||0,public_users:Number(cr[0].public_users)||0,active_now:Number(cr[0].active_now)||0,active_24h:Number(cr[0].active_24h)||0};else v24CommunityStats={state:'ready',total_users:0,public_users:0,active_now:0,active_24h:0};}catch(e){v24CommunityStats={state:'unavailable',total_users:0,public_users:0,active_now:0,active_24h:0};}
      v20RankStatus='ready';v20RankUpdated=Date.now();renderV20();
    }catch(e){v20RankStatus='error';v20RankError='Could not load the public leaderboard. Check backend setup and try Refresh.';v20RankRows=[];v20RankActive=[];v24CommunityStats={state:'unavailable',total_users:0,public_users:0,active_now:0,active_24h:0};renderV20();}
  };

"""
s=s[:ls]+loader+s[le:]

# Final rank UI with community stats + active named users
rs=s.rfind('  function v20Rank(){')
re_end=s.find('\n\n  function v20More(){',rs)
if rs<0 or re_end<0: raise RuntimeError('final v20Rank not found')
rankfn="""  function v20Rank(){
    const local=v20LocalRank(),rows=v20Top20(),q=v20RankQuery.trim().toLowerCase();
    const filtered=rows.filter(x=>String(x.display_name||'').toLowerCase().includes(q));
    const my=v24RankMyGlobal,active=(v20RankActive||[]).slice(0,6),cs=v24CommunityStats||{state:'idle',total_users:0,public_users:0,active_now:0,active_24h:0};
    const communityCard=cs.state==='ready'?'<section class="v24-community-stats"><div><b>'+cs.total_users+'</b><span>Community users</span></div><div><b>'+cs.public_users+'</b><span>Public profiles</span></div><div><b>'+cs.active_now+'</b><span>Active now</span></div><div><b>'+cs.active_24h+'</b><span>Active 24h</span></div></section>':'<section class="v24-community-offline"><b>Community count unavailable</b><span>'+(cs.state==='offline'?'Connect Supabase to see user names and counts.':'Refresh the community data after backend setup.')+'</span></section>';
    const activeCard=active.length?'<section class="v24-community-card"><div class="v20-head"><div><span class="kicker">LIVE COMMUNITY</span><h2>Active right now</h2></div><span class="v24-live-count">● '+(cs.active_now||active.length)+'</span></div><div class="v24-active-list">'+active.map(function(x){return '<div class="v24-active-row"><span class="v24-active-rank">#'+(Number(x.rank)||'—')+'</span><span class="v24-active-avatar">'+escapeHtml((x.display_name||'?').slice(0,1).toUpperCase())+'</span><div><b>'+escapeHtml(x.display_name||'Arc member')+'</b><small>'+Number(x.rank_score||0)+' score · 🔥 '+Number(x.best_streak||0)+'</small></div></div>';}).join('')+'</div></section>':'';
    return `<div class="v24-page"><section class="v24-rank-hero"><div><span class="kicker">ARC LEAGUE</span><h1>${my?.rank?'#'+my.rank:'Top 20'}</h1><p>${my?.rank?'Your exact public rank':'Community Rank is optional and private by default.'}</p></div><div><b>${local.score}</b><span>/100 score</span></div><div class="progress"><i style="width:${local.score}%"></i></div></section>${communityCard}${activeCard}<section class="v24-section"><div class="v20-head"><div><span class="kicker">GLOBAL</span><h2>Top 20</h2></div><button class="v20-refresh" data-v20-rank-refresh aria-label="Refresh leaderboard">↻</button></div><input class="v24-rank-search" id="v20RankSearch" value="${escapeHtml(v20RankQuery)}" placeholder="Search Top 20 by name" aria-label="Search Top 20 by name"><div class="v24-ranklist">${v20RankStatus==='loading'?'<div class="v24-empty"><b>Loading Top 20…</b></div>':v20RankStatus==='offline'||v20RankStatus==='error'?`<div class="v24-empty"><b>${escapeHtml(v20RankError)}</b><span>Local tracker remains fully usable.</span></div>`:filtered.length?filtered.map((x)=>{const rank=x.__rank||v20RankRows.indexOf(x)+1;const name=escapeHtml(x.display_name||'Arc member');const score=Number(x.rankScore??x.rank_score)||0;return `<div class="v24-rank-row ${data.cloudUserId&&x.id===data.cloudUserId?'me':''}"><span class="num">#${rank}</span><span class="avatar">${escapeHtml((x.display_name||'?').slice(0,1).toUpperCase())}</span><div><b>${name}</b><small>${Number(x.total_wins)||0} wins · 🔥 ${Number(x.best_streak)||0} streak</small></div><strong>${score}</strong></div>`}).join(''):'<div class="v24-empty"><b>No public profiles yet.</b><span>Turn on Community Sync + Public Profile to appear.</span></div>'}</div>${v20RankStatus==='ready'?`<div class="v24-rank-foot">${my?.rank?`Your exact public rank: <b>#${my.rank}</b>`:'Your profile is private.'}</div>`:''}</section><section class="note"><b>How scoring works</b><br>75% weekly consistency + 15% best streak + 10% weekly wins. Ties are deterministic.</section></div>`;
  }"""
s=s[:rs]+rankfn+s[re_end:]

# Direct Rank/Profile bottom nav
shell=s.rfind('  function v20Shell(){')
old="    const labels=[['today','🏠','Today'],['week','▦','Week'],['month','🗓️','Month'],['arc','❄️','Arc'],['more','•••','More']];"
new="    const labels=[['today','🏠','Today'],['week','▦','Week'],['rank','🏆','Rank'],['profile','👤','Profile'],['more','•••','More']];"
pos=s.find(old,shell)
if pos<0: raise RuntimeError('shell nav labels not found')
s=s[:pos]+new+s[pos+len(old):]

# Syntax check
compile(app_path.read_text(encoding='utf-8'), 'app.js', 'exec') if False else None
# A lightweight parser check using node
import subprocess, tempfile
with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8') as tf:
    tf.write(s); tmp=tf.name
p=subprocess.run(['node','--check',tmp],capture_output=True,text=True)
Path(tmp).unlink(missing_ok=True)
if p.returncode:
    raise RuntimeError('Patched app.js syntax failed:\n'+p.stderr)

app_path.with_suffix('.js.v24.1-backup').write_text(app_path.read_text(encoding='utf-8'),encoding='utf-8')
app_path.write_text(s,encoding='utf-8')
print('app.js patched and syntax-check passed')
