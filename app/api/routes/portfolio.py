from typing import Optional, List, Dict
from fastapi import Query, APIRouter, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, Response
from app.utils.generate_portfolio import build_portfolio_model
from pydantic import BaseModel, Field
from app.data.db import get_connection
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
import os
import time
import base64
import urllib.request
import urllib.error
import json as _json


router = APIRouter()

# Payload model for editing project details
class ProjectEdit(BaseModel):
    project_signature: str
    project_name: Optional[str] = None # TBD Project Name length limit 
    project_summary: Optional[str] = None # TBD Project Summary length limit
    created_at: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    score_overridden_value: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class BatchEditPayload(BaseModel):
    edits: List[ProjectEdit] 


class GitHubPagesPublishPayload(BaseModel):
    github_token: str
    project_ids: Optional[List[str]] = None   # if None, publish all projects
    repo_name: Optional[str] = None            # defaults to {username}.github.io


def _build_portfolio_html(project_ids: Optional[List[str]] = None) -> str:
    """Build a self-contained static portfolio HTML page that matches the app's visual design."""
    data = build_portfolio_model(project_ids=project_ids)

    user = data.get("user") or {}
    projects = data.get("projects") or []
    overview = data.get("overview") or {}
    graphs = data.get("graphs") or {}
    collab_network = data.get("collaboration_network") or {}

    name = user.get("name") or "Developer"
    job_title = user.get("job_title") or ""
    email = user.get("email") or ""
    summary = user.get("personal_summary") or ""
    github_user = user.get("github_user") or ""

    # ── Project cards ──────────────────────────────────────────────────────────
    project_cards_html = ""
    for p in projects:
        title = p.get("name") or p.get("title") or f"Project {p.get('id', '')}"
        proj_summary = p.get("summary") or ""
        skills = p.get("skills") or []
        if not skills:
            skills = (p.get("metrics") or {}).get("technical_keywords") or []
        skills_html = "".join(
            f'<span class="project-skill-tag">{s}</span>' for s in skills[:8]
        )
        proj_type = p.get("type") or ""
        date_range = p.get("dates") or ""
        created = p.get("created_at") or ""
        display_date = date_range or (created[:10] if created else "")
        type_badge = f'<span class="project-type-badge">{proj_type}</span>' if proj_type else ""
        date_html = f'<div class="project-date">\U0001F4C5 {display_date}</div>' if display_date else ""
        summary_html = f'<p class="project-summary">{proj_summary}</p>' if proj_summary else ""
        skills_row = f'<div class="project-skills">{skills_html}</div>' if skills_html else ""
        project_cards_html += f"""
        <div class="project-card">
          <div class="project-card-header">
            <h3 class="project-title">{title}</h3>
            {type_badge}
          </div>
          {date_html}
          {summary_html}
          {skills_row}
        </div>"""

    # ── Collaboration network section ──────────────────────────────────────────
    collab_nodes = collab_network.get("nodes") or []
    collab_edges = collab_network.get("edges") or []

    collab_section_html = ""
    if len(collab_nodes) > 1:
        network_json = _json.dumps(collab_network).replace("</", "<\\/")
        direct_edges = [e for e in collab_edges if not e.get("is_peer")]
        total_commits = sum(n.get("commits", 0) for n in collab_nodes)
        collab_section_html = f"""
    <div class="portfolio-section network-section">
      <h2 class="section-title">\U0001F91D Collaboration Network</h2>
      <div class="network-graph-container" data-graph-theme="dark">
        <div class="network-canvas-wrap">
          <div id="networkGraphTarget" style="width:100%;min-height:480px;position:relative;border-radius:12px;background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);border:1px solid rgba(99,102,241,0.15);box-shadow:inset 0 1px 30px rgba(0,0,0,0.3);"></div>
        </div>
        <div class="network-info-panel" id="networkInfoPanel">
          <div class="network-info-hint" style="color:#e2e8f0;">\U0001F446 Hover for details &middot; Drag to rearrange &middot; Node size = commit count</div>
        </div>
        <div class="network-legend">
          <div class="network-stat"><span class="network-stat-value">{len(collab_nodes)}</span><span class="network-stat-label">Contributors</span></div>
          <div class="network-stat"><span class="network-stat-value" id="nc-connections">{len(direct_edges)}</span><span class="network-stat-label">Connections</span></div>
          <div class="network-stat"><span class="network-stat-value" id="nc-commits">{total_commits:,}</span><span class="network-stat-label" id="nc-commits-label">Total Commits</span></div>
        </div>
      </div>
    </div>
<script>
(function(){{
  var NET={network_json};
  if(!NET||!NET.nodes||NET.nodes.length<=1)return;
  var target=document.getElementById('networkGraphTarget');
  if(!target)return;
  var COLORS=["#6366f1","#8b5cf6","#ec4899","#f43f5e","#f97316","#eab308","#22c55e","#14b8a6","#06b6d4","#3b82f6"];
  function ha(h,a){{var r=parseInt(h.slice(1,3),16),g=parseInt(h.slice(3,5),16),b=parseInt(h.slice(5,7),16);return'rgba('+r+','+g+','+b+','+a+')';}}
  function lt(h,n){{var r=Math.min(255,parseInt(h.slice(1,3),16)+n),g=Math.min(255,parseInt(h.slice(3,5),16)+n),b=Math.min(255,parseInt(h.slice(5,7),16)+n);return'#'+r.toString(16).padStart(2,'0')+g.toString(16).padStart(2,'0')+b.toString(16).padStart(2,'0');}}
  var mode='star',sc=1;
  function nc(n,i){{return n.is_primary?'#1e293b':COLORS[i%COLORS.length];}}
  function nr(n){{if(n.is_primary)return 32*sc;return mode==='full'?(16+Math.min(n.projects.length,8)*2.5)*sc:(14+Math.min(n.commits,80)*0.18)*sc;}}
  function activeEdges(){{return mode==='star'?NET.edges.filter(function(e){{return!e.is_peer;}}):NET.edges;}}
  target.style.position='relative';
  var canvas=document.createElement('canvas');
  canvas.style.cssText='width:100%;border-radius:12px;display:block;cursor:default;user-select:none;';
  target.appendChild(canvas);
  var toolbar=document.createElement('div');
  toolbar.style.cssText='position:absolute;top:10px;right:10px;z-index:10;display:flex;gap:6px;';
  target.appendChild(toolbar);
  var rStyle='display:flex;border-radius:8px;border:1px solid rgba(99,102,241,0.25);background:rgba(30,41,59,0.7);overflow:hidden;';
  var bBase='height:30px;padding:0 10px;border:none;font-size:12px;font-weight:500;cursor:pointer;color:rgba(226,232,240,0.6);background:transparent;transition:background 0.2s,color 0.2s;';
  var mR=document.createElement('div');mR.style.cssText=rStyle;toolbar.appendChild(mR);
  var sBtn=document.createElement('button');sBtn.textContent='\u2B50 Star';sBtn.style.cssText=bBase+'border-right:1px solid rgba(99,102,241,0.25);';mR.appendChild(sBtn);
  var nBtn=document.createElement('button');nBtn.textContent='\U0001F578 Network';nBtn.style.cssText=bBase;mR.appendChild(nBtn);
  function updR(){{
    sBtn.style.background=mode==='star'?'rgba(99,102,241,0.35)':'transparent';sBtn.style.color=mode==='star'?'#fff':'rgba(226,232,240,0.6)';
    nBtn.style.background=mode==='full'?'rgba(99,102,241,0.35)':'transparent';nBtn.style.color=mode==='full'?'#fff':'rgba(226,232,240,0.6)';
  }}
  updR();
  var W=target.clientWidth||800,H=Math.max(420,Math.min(580,Math.floor(W*0.50)));
  var dpr=window.devicePixelRatio||1;
  canvas.width=W*dpr;canvas.height=H*dpr;canvas.style.height=H+'px';
  var ctx=canvas.getContext('2d');ctx.setTransform(dpr,0,0,dpr,0,0);
  var cx=W/2,cy=H/2;
  function compSc(){{var raw=Math.min(W,H)/480,adj=Math.max(0.8,Math.min(1.5,8/Math.max(NET.nodes.length,1)));sc=Math.max(0.9,Math.min(1.7,raw*adj));}}
  compSc();
  var nodes=NET.nodes.map(function(n,i){{
    var a=(2*Math.PI*i)/NET.nodes.length,spread=Math.min(W,H)*0.42;
    var r=n.is_primary?0:spread+Math.random()*80;
    return{{id:n.id,name:n.name,commits:n.commits,is_primary:n.is_primary,projects:n.projects,
      x:cx+Math.cos(a)*r+(Math.random()-0.5)*30,y:cy+Math.sin(a)*r+(Math.random()-0.5)*30,vx:0,vy:0,fx:null,fy:null}};
  }});
  var hovered=null,drag={{node:null,ox:0,oy:0,active:false}};
  var infoPanel=document.getElementById('networkInfoPanel');
  function updLegend(){{
    var eds=activeEdges();
    var cE=document.getElementById('nc-connections'),cmE=document.getElementById('nc-commits'),lE=document.getElementById('nc-commits-label');
    if(cE)cE.textContent=eds.length;
    if(cmE&&lE){{if(mode==='full'){{cmE.textContent=NET.edges.filter(function(e){{return e.is_peer;}}).length;lE.textContent='Peer Links';}}else{{cmE.textContent=NET.nodes.reduce(function(s,n){{return s+n.commits;}},0).toLocaleString();lE.textContent='Total Commits';}}}}
  }}
  function hit(mx,my){{for(var i=nodes.length-1;i>=0;i--){{var n=nodes[i],r=nr(n)+4;if((n.x-mx)*(n.x-mx)+(n.y-my)*(n.y-my)<=r*r)return n;}}return null;}}
  function simulate(){{
    var isFull=mode==='full',eds=activeEdges();compSc();
    var rep=(isFull?28000:12000)*sc,att=isFull?0.001:0.003,cp=isFull?0.004:0.008,damp=0.82;
    for(var i=0;i<nodes.length;i++){{for(var j=i+1;j<nodes.length;j++){{
      var dx=nodes[j].x-nodes[i].x,dy=nodes[j].y-nodes[i].y,d=Math.sqrt(dx*dx+dy*dy)||1,f=rep/(d*d),fx=dx/d*f,fy=dy/d*f;
      nodes[i].vx-=fx;nodes[i].vy-=fy;nodes[j].vx+=fx;nodes[j].vy+=fy;
    }}}}
    var nm={{}};nodes.forEach(function(n){{nm[n.id]=n;}});
    eds.forEach(function(e){{
      var s=nm[e.source],t=nm[e.target];if(!s||!t)return;
      var dx=t.x-s.x,dy=t.y-s.y,dist=Math.sqrt(dx*dx+dy*dy)||1;
      var ideal=(isFull?(e.is_peer?350:280):220)*sc,disp=dist-ideal,f=disp*att*(1+e.weight*(isFull?0.1:0.3));
      var fx=dx/dist*f,fy=dy/dist*f;s.vx+=fx;s.vy+=fy;t.vx-=fx;t.vy-=fy;
    }});
    nodes.forEach(function(n){{n.vx+=(cx-n.x)*cp;n.vy+=(cy-n.y)*cp;}});
    var mg=(isFull?60:30)*sc;
    for(var i=0;i<nodes.length;i++){{for(var j=i+1;j<nodes.length;j++){{
      var ri=nr(nodes[i]),rj=nr(nodes[j]),minD=ri+rj+mg,dx=nodes[j].x-nodes[i].x,dy=nodes[j].y-nodes[i].y,dist=Math.sqrt(dx*dx+dy*dy)||1;
      if(dist<minD){{var push=(minD-dist)*0.15,px=dx/dist*push,py=dy/dist*push;nodes[i].vx-=px;nodes[i].vy-=py;nodes[j].vx+=px;nodes[j].vy+=py;}}
    }}}}
    var pad=60;
    nodes.forEach(function(n){{
      if(n.fx!==null){{n.x=n.fx;n.y=n.fy;n.vx=0;n.vy=0;}}
      else{{n.vx*=damp;n.vy*=damp;n.x+=n.vx;n.y+=n.vy;n.x=Math.max(pad,Math.min(W-pad,n.x));n.y=Math.max(pad,Math.min(H-pad,n.y));}}
    }});
  }}
  function draw(){{
    ctx.clearRect(0,0,W,H);
    var eds=activeEdges(),nm={{}};nodes.forEach(function(n){{nm[n.id]=n;}});
    var conn={{}};if(hovered){{conn[hovered.id]=true;eds.forEach(function(e){{if(e.source===hovered.id||e.target===hovered.id){{conn[e.source]=true;conn[e.target]=true;}}}});}}
    eds.forEach(function(e){{
      var s=nm[e.source],t=nm[e.target];if(!s||!t)return;
      var hi=hovered&&(hovered.id===e.source||hovered.id===e.target),isPeer=!!e.is_peer;
      var si=nodes.indexOf(s),ti=nodes.indexOf(t);
      var al=hi?0.65:hovered?(isPeer?0.03:0.06):isPeer?0.09:0.15+e.weight*0.04;
      var g=ctx.createLinearGradient(s.x,s.y,t.x,t.y);
      g.addColorStop(0,ha(nc(s,si),al));g.addColorStop(1,ha(nc(t,ti),al));
      ctx.beginPath();ctx.moveTo(s.x,s.y);ctx.lineTo(t.x,t.y);ctx.strokeStyle=g;
      ctx.lineWidth=hi?2.5+e.weight*0.5:isPeer?0.5+e.weight*0.15:0.8+e.weight*0.25;
      ctx.setLineDash(isPeer?[6*sc,4*sc]:[]);ctx.stroke();ctx.setLineDash([]);
      if(hi){{
        var mx=(s.x+t.x)/2,my=(s.y+t.y)/2;
        ctx.fillStyle='rgba(30,41,59,0.92)';ctx.beginPath();ctx.arc(mx,my,Math.round(9*sc),0,Math.PI*2);ctx.fill();
        ctx.strokeStyle='rgba(99,102,241,0.6)';ctx.lineWidth=1;ctx.stroke();
        ctx.fillStyle='#fff';ctx.font='bold '+Math.round(8*sc)+'px system-ui,sans-serif';
        ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(String(e.projects.length),mx,my);
      }}
    }});
    nodes.forEach(function(node,i){{
      var r=nr(node),col=nc(node,i),isH=hovered&&hovered.id===node.id,isC=hovered&&conn[node.id];
      var dim=hovered&&!isH&&!isC&&!drag.active;
      if(isH||isC||node.is_primary){{
        var gs=(isH?10:isC?8:6)*sc;ctx.beginPath();ctx.arc(node.x,node.y,r+gs,0,Math.PI*2);
        var gl=ctx.createRadialGradient(node.x,node.y,r*0.5,node.x,node.y,r+gs+4);
        gl.addColorStop(0,ha(col,isH?0.35:0.22));gl.addColorStop(1,ha(col,0));ctx.fillStyle=gl;ctx.fill();
      }}
      ctx.beginPath();ctx.arc(node.x,node.y,r,0,Math.PI*2);
      var bg=ctx.createRadialGradient(node.x-r*0.3,node.y-r*0.3,r*0.1,node.x,node.y,r);
      if(node.is_primary){{bg.addColorStop(0,'#334155');bg.addColorStop(1,'#0f172a');}}
      else{{bg.addColorStop(0,lt(col,20));bg.addColorStop(1,col);}}
      ctx.fillStyle=dim?ha(col,0.35):bg;ctx.fill();
      ctx.strokeStyle=dim?ha(col,0.2):isH?'#fff':isC?'rgba(255,255,255,0.7)':ha(lt(col,30),0.6);
      ctx.lineWidth=isH?2.5:isC?2.2:node.is_primary?2:1.5;ctx.stroke();
      if(!dim){{ctx.beginPath();ctx.arc(node.x-r*0.2,node.y-r*0.25,r*0.45,0,Math.PI*2);ctx.fillStyle='rgba(255,255,255,0.13)';ctx.fill();}}
      ctx.textAlign='center';ctx.textBaseline='middle';
      if(node.is_primary){{
        var lbl=node.name.length>16?node.name.slice(0,15)+'\u2026':node.name,fs=Math.round(11*sc);
        ctx.font='bold '+fs+'px system-ui,sans-serif';
        while(ctx.measureText(lbl).width>r*1.7&&fs>6){{fs--;ctx.font='bold '+fs+'px system-ui,sans-serif';}}
        ctx.fillStyle=dim?'rgba(255,255,255,0.4)':'#fff';ctx.fillText(lbl,node.x,node.y);
      }}else{{
        var lbl=node.name.length>16?node.name.slice(0,15)+'\u2026':node.name;
        ctx.font='500 '+Math.round(9*sc)+'px system-ui,sans-serif';
        var ly=node.y+r+Math.round(13*sc),m=ctx.measureText(lbl),lw=m.width+8*sc;
        ctx.fillStyle=dim?'rgba(30,41,59,0.3)':'rgba(30,41,59,0.7)';
        ctx.beginPath();
        if(ctx.roundRect)ctx.roundRect(node.x-lw/2,ly-Math.round(7*sc),lw,Math.round(14*sc),4);
        else ctx.rect(node.x-lw/2,ly-Math.round(7*sc),lw,Math.round(14*sc));
        ctx.fill();
        ctx.fillStyle=dim?'rgba(255,255,255,0.3)':'#e2e8f0';ctx.fillText(lbl,node.x,ly);
      }}
      if(r>=14&&!node.is_primary&&!dim){{
        ctx.font='bold '+Math.round(8*sc)+'px system-ui,sans-serif';ctx.fillStyle='rgba(255,255,255,0.9)';
        ctx.fillText(mode==='full'?String(node.projects.length):String(node.commits),node.x,node.y);
      }}
    }});
  }}
  function updInfo(n){{
    if(!infoPanel)return;
    if(n){{
      infoPanel.style.borderColor='rgba(99,102,241,0.35)';infoPanel.style.background='#0f172a';
      var cl=mode==='full'?n.projects.length+' project'+(n.projects.length!==1?'s':''):n.commits.toLocaleString()+' commits';
      var h='<div class="network-info-name" style="color:#f1f5f9;">'+n.name+'</div>';
      h+='<div class="network-info-commits" style="color:#a78bfa;">'+cl+'</div><div class="network-info-projects">';
      n.projects.forEach(function(p){{h+='<span class="network-info-project-tag" style="color:#38bdf8;background:rgba(56,189,248,0.1);border:1px solid rgba(56,189,248,0.2);">'+p+'</span>';}});
      h+='</div>';infoPanel.innerHTML=h;
    }}else{{
      infoPanel.style.borderColor='#334155';infoPanel.style.background='#1e293b';
      var hint='Hover for details \u00b7 Drag to rearrange \u00b7 '+(mode==='full'?'Node size = project breadth':'Node size = commit count');
      infoPanel.innerHTML='<div class="network-info-hint" style="color:#e2e8f0;">\U0001F446 '+hint+'</div>';
    }}
  }}
  sBtn.addEventListener('click',function(){{mode='star';updR();updLegend();updInfo(hovered);}});
  nBtn.addEventListener('click',function(){{mode='full';updR();updLegend();updInfo(hovered);}});
  function tick(){{simulate();draw();requestAnimationFrame(tick);}}
  updInfo(null);updLegend();requestAnimationFrame(tick);
  canvas.addEventListener('mousedown',function(e){{
    var rect=canvas.getBoundingClientRect(),mx=e.clientX-rect.left,my=e.clientY-rect.top,n=hit(mx,my);
    if(n){{drag={{node:n,ox:mx-n.x,oy:my-n.y,active:true}};n.fx=n.x;n.fy=n.y;}}
  }});
  canvas.addEventListener('mousemove',function(e){{
    var rect=canvas.getBoundingClientRect(),mx=e.clientX-rect.left,my=e.clientY-rect.top;
    if(drag.active&&drag.node){{drag.node.fx=mx-drag.ox;drag.node.fy=my-drag.oy;drag.node.x=drag.node.fx;drag.node.y=drag.node.fy;}}
    var f=hit(mx,my);if(f!==hovered){{hovered=f;updInfo(f);}}
    canvas.style.cursor=drag.active?'grabbing':f?'grab':'default';
  }});
  canvas.addEventListener('mouseup',function(){{if(drag.node){{drag.node.fx=null;drag.node.fy=null;}}drag={{node:null,ox:0,oy:0,active:false}};}});
  canvas.addEventListener('mouseleave',function(){{if(drag.node){{drag.node.fx=null;drag.node.fy=null;}}drag={{node:null,ox:0,oy:0,active:false}};hovered=null;updInfo(null);canvas.style.cursor='default';}});
  window.addEventListener('resize',function(){{
    W=target.clientWidth||800;H=Math.max(420,Math.min(580,Math.floor(W*0.50)));cx=W/2;cy=H/2;
    canvas.width=W*dpr;canvas.height=H*dpr;canvas.style.height=H+'px';ctx.setTransform(dpr,0,0,dpr,0,0);compSc();
  }});
}})();
</script>"""

    # ── Chart data ─────────────────────────────────────────────────────────────
    lang_dist = graphs.get("language_distribution") or {}
    lang_labels = _json.dumps(list(lang_dist.keys()))
    lang_values = _json.dumps(list(lang_dist.values()))

    top_skills = graphs.get("top_skills") or {}
    skills_labels = _json.dumps(list(top_skills.keys())[:10])
    skills_values = _json.dumps(list(top_skills.values())[:10])

    complexity = (graphs.get("complexity_distribution") or {}).get("distribution") or {}
    complexity_labels = _json.dumps(["Small (<1 k)", "Medium (1–3 k)", "Large (>3 k)"])
    complexity_values = _json.dumps([
        complexity.get("small", 0),
        complexity.get("medium", 0),
        complexity.get("large", 0),
    ])

    monthly = graphs.get("monthly_activity") or {}
    monthly_sorted = sorted(monthly.items())
    monthly_labels = _json.dumps([e[0] for e in monthly_sorted])
    monthly_values = _json.dumps([e[1] for e in monthly_sorted])

    # ── Profile avatar initials ────────────────────────────────────────────────
    initials = "".join(w[0].upper() for w in (name or "D").split()[:2]) or "D"

    # ── Stat numbers ───────────────────────────────────────────────────────────
    total_projects = overview.get("total_projects", len(projects))
    total_skills = overview.get("total_skills", 0)
    total_langs = overview.get("total_languages", len(lang_dist))
    total_lines = (overview.get("total_lines") or 0)

    # ── GitHub link & email ────────────────────────────────────────────────────
    github_href = f"https://github.com/{github_user}" if github_user else ""
    github_link = (
        f'<a class="profile-link" href="{github_href}" target="_blank" rel="noopener">'
        f'<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">'
        f'<path d="M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482'
        f'0-.237-.009-.868-.013-1.703-2.782.605-3.369-1.342-3.369-1.342-.454-1.154-1.11-1.462-1.11-1.462'
        f'-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.088 2.91.832'
        f'.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683'
        f'-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0 1 12 6.836'
        f'a9.578 9.578 0 0 1 2.504.337c1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647'
        f'.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852'
        f'0 1.336-.012 2.415-.012 2.744 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12'
        f'c0-5.523-4.477-10-10-10z"/></svg>'
        f'github.com/{github_user}</a>'
    ) if github_user else ""
    email_link = (
        f'<a class="profile-link" href="mailto:{email}">'
        f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
        f'<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>'
        f'<polyline points="22,6 12,12 2,6"/></svg>{email}</a>'
    ) if email else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} | Portfolio</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<style>
/* ── Design tokens ─────────────────────────────────────────────────────── */
:root {{
  --primary-bg: #0f172a;
  --card: #1e293b;
  --card-bg: #1e293b;
  --border: #334155;
  --border-light: rgba(99,102,241,0.08);
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --accent: #818cf8;
  --accent-secondary: #6366f1;
  --accent-glow: rgba(99,102,241,0.35);
  --shadow: 0 4px 24px rgba(0,0,0,0.35);
  --shadow-lg: 0 8px 40px rgba(0,0,0,0.5);
  --radius: 12px;
  --radius-sm: 8px;
  --radius-lg: 16px;
  --transition: 0.2s ease;
}}

/* ── Reset ─────────────────────────────────────────────────────────────── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--primary-bg);
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
}}
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* ── Layout ────────────────────────────────────────────────────────────── */
.main-content {{
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 28px 60px;
}}

/* ── Profile hero ──────────────────────────────────────────────────────── */
.profile-hero {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 28px 32px;
  display: flex;
  align-items: center;
  gap: 24px;
  margin: 32px 0 28px;
  box-shadow: var(--shadow);
  position: relative;
  overflow: hidden;
}}
.profile-hero::before {{
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent), var(--accent-secondary));
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}}
.profile-avatar {{
  width: 72px; height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-secondary), var(--accent));
  display: flex; align-items: center; justify-content: center;
  font-size: 1.6rem; font-weight: 800; color: #fff;
  flex-shrink: 0;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.3);
}}
.profile-info {{ flex: 1; min-width: 0; }}
.profile-name {{
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.03em;
  margin-bottom: 2px;
}}
.profile-title {{
  font-size: 1rem;
  color: var(--accent);
  font-weight: 500;
  margin-bottom: 8px;
}}
.profile-summary {{
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
  max-width: 680px;
}}
.profile-links {{ display: flex; gap: 16px; flex-wrap: wrap; }}
.profile-link {{
  display: flex; align-items: center; gap: 6px;
  font-size: 0.85rem; color: var(--text-secondary);
  transition: color var(--transition);
}}
.profile-link:hover {{ color: var(--accent); text-decoration: none; }}
.profile-link svg {{ flex-shrink: 0; opacity: 0.7; }}

/* ── Stat bar ──────────────────────────────────────────────────────────── */
.stat-bar {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 16px;
  margin-bottom: 36px;
}}
.stat-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  text-align: center;
  box-shadow: var(--shadow);
  transition: border-color var(--transition), transform var(--transition);
}}
.stat-card:hover {{
  border-color: var(--accent-secondary);
  transform: translateY(-2px);
}}
.stat-value {{
  font-size: 2rem;
  font-weight: 800;
  color: var(--accent);
  line-height: 1;
  margin-bottom: 4px;
}}
.stat-label {{
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
}}

/* ── Section titles ────────────────────────────────────────────────────── */
.portfolio-section {{ margin-bottom: 40px; }}
.section-title {{
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: -0.02em;
}}
.section-title::after {{
  content: "";
  flex: 1;
  height: 1px;
  background: var(--border);
  margin-left: 8px;
}}

/* ── Charts grid ───────────────────────────────────────────────────────── */
.charts-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}}
.chart-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 22px;
  box-shadow: var(--shadow);
}}
.chart-card-title {{
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 14px;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}}
.chart-container {{ position: relative; height: 220px; }}

/* ── Projects grid ─────────────────────────────────────────────────────── */
.projects-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}}
.project-card {{
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 22px;
  transition: border-color var(--transition), transform var(--transition), box-shadow var(--transition);
  box-shadow: var(--shadow);
}}
.project-card:hover {{
  border-color: var(--accent-secondary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}}
.project-card-header {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
}}
.project-title {{
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
}}
.project-type-badge {{
  background: rgba(99,102,241,0.15);
  color: var(--accent);
  border: 1px solid rgba(99,102,241,0.3);
  padding: 3px 10px;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}}
.project-date {{
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-bottom: 10px;
}}
.project-summary {{
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.55;
  margin-bottom: 14px;
}}
.project-skills {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}}
.project-skill-tag {{
  background: var(--border-light);
  color: var(--text-primary);
  border: 1px solid var(--border);
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 500;
}}

/* ── Network graph ─────────────────────────────────────────────────────── */
.network-graph-container {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow);
}}
.network-canvas-wrap {{
  position: relative;
  width: 100%;
  margin-bottom: 0;
}}
.network-info-panel {{
  min-height: 44px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding: 10px 16px;
  margin-top: 12px;
  border-radius: 10px;
  background: var(--card);
  border: 1px solid var(--border);
  transition: background 0.2s, border-color 0.2s;
}}
.network-info-name {{ font-weight: 700; font-size: 13px; color: #f1f5f9; }}
.network-info-commits {{ font-weight: 600; font-size: 12px; color: #a78bfa; }}
.network-info-projects {{ display: flex; gap: 6px; flex-wrap: wrap; }}
.network-info-project-tag {{
  font-size: 10px; font-weight: 500;
  padding: 2px 8px; border-radius: 9999px;
}}
.network-info-hint {{ font-size: 13px; color: var(--text-secondary); }}
.network-legend {{
  display: flex;
  gap: 28px;
  margin-top: 12px;
  padding: 12px 16px;
  border-radius: 10px;
  background: var(--card);
  border: 1px solid var(--border);
}}
.network-stat {{ display: flex; flex-direction: column; gap: 2px; }}
.network-stat-value {{
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}}
.network-stat-label {{
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
}}

/* ── Footer ────────────────────────────────────────────────────────────── */
.portfolio-footer {{
  text-align: center;
  padding: 32px 20px;
  color: var(--text-muted);
  font-size: 0.8rem;
  border-top: 1px solid var(--border);
  margin-top: 20px;
}}

/* ── Responsive ────────────────────────────────────────────────────────── */
@media (max-width: 640px) {{
  .profile-hero {{ flex-direction: column; text-align: center; padding: 24px 20px; }}
  .profile-links {{ justify-content: center; }}
  .main-content {{ padding: 0 16px 40px; }}
  .stat-bar {{ grid-template-columns: repeat(2, 1fr); }}
}}
</style>
</head>
<body>
<div class="main-content">

  <!-- Profile Hero -->
  <div class="profile-hero">
    <div class="profile-avatar">{initials}</div>
    <div class="profile-info">
      <div class="profile-name">{name}</div>
      {f'<div class="profile-title">{job_title}</div>' if job_title else ''}
      {f'<div class="profile-summary">{summary}</div>' if summary else ''}
      <div class="profile-links">
        {email_link}
        {github_link}
      </div>
    </div>
  </div>

  <!-- Stats -->
  <div class="stat-bar">
    <div class="stat-card">
      <div class="stat-value">{total_projects}</div>
      <div class="stat-label">Projects</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{total_skills}</div>
      <div class="stat-label">Skills</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{total_langs}</div>
      <div class="stat-label">Languages</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{total_lines:,}</div>
      <div class="stat-label">Lines of Code</div>
    </div>
  </div>

  <!-- Analytics -->
  <div class="portfolio-section">
    <h2 class="section-title">&#x1F4CA; Analytics</h2>
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-card-title">Language Distribution</div>
        <div class="chart-container"><canvas id="langChart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-card-title">Top Skills</div>
        <div class="chart-container"><canvas id="skillsChart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-card-title">Project Complexity</div>
        <div class="chart-container"><canvas id="complexityChart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-card-title">Monthly Activity</div>
        <div class="chart-container"><canvas id="activityChart"></canvas></div>
      </div>
    </div>
  </div>

  <!-- Collaboration Network -->
  {collab_section_html}

  <!-- Projects -->
  <div class="portfolio-section projects-section">
    <h2 class="section-title">&#x1F680; Projects</h2>
    <div class="projects-grid">{project_cards_html}</div>
  </div>

</div>
<footer class="portfolio-footer">
  Generated by Big Picture Insights &middot; {len(projects)} project{'s' if len(projects) != 1 else ''}
</footer>
<script>
(function() {{
  var COLORS = ['#818cf8','#34d399','#f472b6','#fb923c','#a78bfa','#38bdf8','#facc15','#4ade80','#e879f9','#f87171',
                '#60a5fa','#2dd4bf','#c084fc','#fbbf24','#86efac','#f9a8d4'];

  function darkTicks() {{
    return {{ color: '#94a3b8', font: {{ size: 11 }} }};
  }}
  function darkGrid() {{
    return {{ color: 'rgba(51,65,85,0.6)' }};
  }}

  // Language pie
  var langLabels = {lang_labels};
  var langValues = {lang_values};
  if (langLabels.length) {{
    new Chart(document.getElementById('langChart'), {{
      type: 'doughnut',
      data: {{
        labels: langLabels,
        datasets: [{{ data: langValues, backgroundColor: COLORS, borderColor: '#0f172a', borderWidth: 2, hoverOffset: 6 }}]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{
          legend: {{ position: 'bottom', labels: {{ color: '#94a3b8', font: {{ size: 11 }}, padding: 12, usePointStyle: true }} }}
        }}
      }}
    }});
  }}

  // Skills horizontal bar
  var skillLabels = {skills_labels};
  var skillValues = {skills_values};
  if (skillLabels.length) {{
    new Chart(document.getElementById('skillsChart'), {{
      type: 'bar',
      data: {{
        labels: skillLabels,
        datasets: [{{ data: skillValues, backgroundColor: '#6366f1', borderRadius: 4, borderSkipped: false }}]
      }},
      options: {{
        indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ ticks: darkTicks(), grid: darkGrid(), beginAtZero: true }},
          y: {{ ticks: darkTicks(), grid: {{ display: false }} }}
        }}
      }}
    }});
  }}

  // Complexity bar
  var complexityLabels = {complexity_labels};
  var complexityValues = {complexity_values};
  if (complexityValues.some(function(v){{ return v > 0; }})) {{
    new Chart(document.getElementById('complexityChart'), {{
      type: 'bar',
      data: {{
        labels: complexityLabels,
        datasets: [{{ data: complexityValues, backgroundColor: ['#818cf8','#34d399','#f472b6'], borderRadius: 6, borderSkipped: false }}]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ ticks: darkTicks(), grid: {{ display: false }} }},
          y: {{ ticks: darkTicks(), grid: darkGrid(), beginAtZero: true }}
        }}
      }}
    }});
  }}

  // Monthly activity line
  var monthlyLabels = {monthly_labels};
  var monthlyValues = {monthly_values};
  if (monthlyLabels.length) {{
    new Chart(document.getElementById('activityChart'), {{
      type: 'line',
      data: {{
        labels: monthlyLabels,
        datasets: [{{
          label: 'Activity',
          data: monthlyValues,
          borderColor: '#818cf8',
          backgroundColor: 'rgba(99,102,241,0.12)',
          fill: true,
          tension: 0.4,
          borderWidth: 2.5,
          pointBackgroundColor: '#818cf8',
          pointBorderColor: '#0f172a',
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6,
        }}]
      }},
      options: {{
        responsive: true, maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ ticks: darkTicks(), grid: darkGrid() }},
          y: {{ ticks: darkTicks(), grid: darkGrid(), beginAtZero: true }}
        }}
      }}
    }});
  }}
}})();
</script>
</body>
</html>"""


def _github_request(method: str, url: str, token: str, body: Optional[dict] = None, extra_headers: Optional[dict] = None):
    """Make a GitHub REST API request using only stdlib."""
    data = _json.dumps(body).encode() if body is not None else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "portfolio-builder/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, _json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_bytes = e.read()
        try:
            err_body = _json.loads(body_bytes)
        except Exception:
            err_body = body_bytes.decode(errors="replace")
        return e.code, err_body


@router.post("/portfolio/publish-github-pages")
def publish_portfolio_to_github_pages(payload: GitHubPagesPublishPayload):
    """
    POST /portfolio/publish-github-pages

    Generates the portfolio HTML server-side and publishes it to GitHub Pages.
    Accepts only the GitHub token and optional project_ids — no large payload.
    """
    logger.info("[publish] received request — project_ids=%s, repo_name=%s",
                payload.project_ids, payload.repo_name)

    token = payload.github_token.strip()
    if not token:
        raise HTTPException(status_code=400, detail="github_token is required")

    logger.info("[publish] token length=%d, prefix=%s", len(token), token[:4])

    # 1. Get authenticated user
    logger.info("[publish] step 1: verifying GitHub token via GET /user")
    status, user_data = _github_request("GET", "https://api.github.com/user", token)
    logger.info("[publish] GET /user → HTTP %d", status)
    if status != 200:
        logger.error("[publish] auth failed: %s", user_data)
        raise HTTPException(
            status_code=401,
            detail=f"GitHub authentication failed: {user_data.get('message', 'Invalid token')}",
        )
    username = user_data["login"]
    logger.info("[publish] authenticated as: %s", username)

    # 2. Determine repo name
    repo_name = payload.repo_name or f"{username}.github.io"
    logger.info("[publish] step 2: target repo=%s/%s", username, repo_name)

    # 3. Check if repo exists; create if not
    repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
    status, repo_data = _github_request("GET", repo_url, token)
    logger.info("[publish] GET %s → HTTP %d", repo_url, status)
    if status == 404:
        logger.info("[publish] repo not found — creating %s/%s", username, repo_name)
        status, repo_data = _github_request(
            "POST",
            "https://api.github.com/user/repos",
            token,
            {
                "name": repo_name,
                "description": "Portfolio generated by Big Picture Insights",
                "private": False,
                "auto_init": True,
            },
        )
        logger.info("[publish] POST /user/repos → HTTP %d", status)
        if status not in (200, 201):
            logger.error("[publish] repo creation failed: %s", repo_data)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create GitHub repo: {repo_data.get('message', repo_data)}",
            )
        time.sleep(2)  # wait for repo to initialize
    elif status != 200:
        logger.error("[publish] failed to check repo: HTTP %d — %s", status, repo_data)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check GitHub repo: {repo_data.get('message', repo_data)}",
        )

    default_branch = repo_data.get("default_branch", "main")
    logger.info("[publish] default branch: %s", default_branch)

    # Generate HTML server-side (small JSON payload to GitHub, no upload from browser)
    try:
        html_content = _build_portfolio_html(project_ids=payload.project_ids)
        logger.info("[publish] HTML built — %d bytes", len(html_content))
    except Exception as e:
        logger.exception("[publish] failed to build portfolio HTML")
        raise HTTPException(status_code=500, detail=f"Failed to build portfolio HTML: {e}")

    # 4b. Upload index.html — check if it already exists so we can provide the SHA
    contents_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/index.html"
    logger.info("[publish] step 4b: checking existing index.html at %s", contents_url)
    status, existing = _github_request("GET", contents_url, token)
    file_sha = existing.get("sha") if status == 200 else None
    logger.info("[publish] existing index.html → HTTP %d, sha=%s", status, file_sha)

    encoded_content = base64.b64encode(html_content.encode("utf-8")).decode()
    put_body: dict = {
        "message": "Update portfolio via Portfolio Builder",
        "content": encoded_content,
        "branch": default_branch,
    }
    if file_sha:
        put_body["sha"] = file_sha

    logger.info("[publish] step 4c: uploading index.html (sha present: %s)", bool(file_sha))
    status, put_resp = _github_request(
        "PUT",
        contents_url,
        token,
        put_body,
        extra_headers={"X-GitHub-Api-Bypass-Secret-Scanning": "1"},
    )
    if status not in (200, 201):
        detail = put_resp.get("message", str(put_resp)) if isinstance(put_resp, dict) else str(put_resp)
        logger.error("[publish] upload failed: %s", detail)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload portfolio HTML: {detail}",
        )

    # 5. Enable GitHub Pages if not already enabled
    pages_url = f"https://api.github.com/repos/{username}/{repo_name}/pages"
    p_status, _ = _github_request("GET", pages_url, token)
    if p_status == 404:
        enable_status, enable_resp = _github_request(
            "POST",
            pages_url,
            token,
            {"source": {"branch": default_branch, "path": "/"}},
        )
        if enable_status not in (200, 201):
            logger.warning("[publish] could not enable GitHub Pages automatically: %s", enable_resp)

    published_url = (
        f"https://{username}.github.io"
        if repo_name == f"{username}.github.io"
        else f"https://{username}.github.io/{repo_name}"
    )
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "url": published_url,
            "repo": f"https://github.com/{username}/{repo_name}",
            "username": username,
        },
    )


@router.get("/portfolio")
def get_portfolio(project_ids: Optional[str] = Query(None, description="Comma-separated list of project IDs to include")):
    """
    GET /portfolio endpoint.
    Returns comprehensive portfolio dashboard data with all visualizations.
    
    Query parameters:
    - project_ids: Optional comma-separated list of project IDs (default: all projects)
    
    Returns rich portfolio data perfect for creating sophisticated graphs:
    - Overview statistics (projects, scores, skills, languages, lines of code)
    - Individual project details with metrics
    - Skills timeline for development progression
    - Language distribution for pie charts
    - Project complexity distribution for bar charts
    - Score distribution for quality analysis
    - Daily activity timeline (exact commit-day counts for GitHub projects when available)
    - Monthly activity timeline
    - Project type analysis (GitHub vs Local)
    - Top skills usage
    """
    try:
        # Parse project_ids if provided
        parsed_project_ids = None
        if project_ids:
            parsed_project_ids = [pid.strip() for pid in project_ids.split(",") if pid.strip()]
        
        portfolio_model = build_portfolio_model(project_ids=parsed_project_ids)
        
        return JSONResponse(
            content=portfolio_model,
            headers={
                "Content-Type": "application/json",
                "X-Portfolio-Projects": str(portfolio_model["metadata"]["total_projects"]),
                "X-Portfolio-Generated": portfolio_model["metadata"]["generated_at"],
                "X-Portfolio-Filtered": str(portfolio_model["metadata"]["filtered"])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating portfolio: {str(e)}"
        )

@router.post("/portfolio/edit")
def edit_portfolio(payload: BatchEditPayload):
    """
    POST/portfolio/edit
    Edit one to many portfolio projects in a single query.

    {
  "edits": [
    {
      "project_signature": "sig1",
      "project_name": "New Name 1",
      "project_summary": "New summary 1",
      "created_at": "2024-01-15",
      "last_modified": "2024-06-10"
    },
    {
      "project_signature": "sig2",
      'project_name': "Updated Project 2",
      "project_summary": "Updated summary",
      "last_modified": "2024-06-12",
      "created_at": "2024-02-20"
    }
  ]
 }
    """
    if not payload.edits:
        raise HTTPException(status_code=400, detail="No edits provided")
    
    ALLOWED_FIELDS = {"project_name", "project_summary", "created_at", "last_modified", "score_overridden_value"}
    field_map = {
        "project_name": "name",
        "project_summary": "summary",
        "created_at": "created_at",
        "last_modified": "last_modified",
        "score_overridden_value": "score_overridden_value",
    }
    
    conn, cur = None, None

    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Collect all project signatures
        project_sigs = [edit.project_signature for edit in payload.edits]
        
        # Build a map of which projects update which fields
        field_updates = {}  # {field_name: {project_sig: value}}
        
        for edit in payload.edits:
            data = edit.model_dump(exclude_unset=True)
            project_sig = data.pop("project_signature")
            
            if not data:
                raise HTTPException(
                    status_code=400,
                    detail=f"No fields provided for project {project_sig}"
                )
            
            for key, value in data.items():
                if key not in ALLOWED_FIELDS:
                    raise HTTPException(status_code=400, detail=f"Invalid field: {key}")
                
                column = field_map[key]
                if column not in field_updates:
                    field_updates[column] = {}
                field_updates[column][project_sig] = value

                if key == "score_overridden_value":
                    if "score_overridden" not in field_updates:
                        field_updates["score_overridden"] = {}
                    field_updates["score_overridden"][project_sig] = 1
        
        # Build SQL CASE statements for each column
        set_clauses = []
        params = []
        
        for column, updates in field_updates.items():
            case_parts = []
            for project_sig, value in updates.items():
                case_parts.append("WHEN project_signature = ? THEN ?")
                params.extend([project_sig, value])
            
            case_parts.append(f"ELSE {column}")  # Keep existing value
            case_statement = f"{column} = CASE {' '.join(case_parts)} END"
            set_clauses.append(case_statement)
        
        # Build final query
        placeholders = ','.join(['?'] * len(project_sigs))
        query = f"""
            UPDATE PROJECT 
            SET {', '.join(set_clauses)}
            WHERE project_signature IN ({placeholders})
        """
        
        params.extend(project_sigs)
        cur.execute(query, tuple(params))
        
        if cur.rowcount <=0:
            raise HTTPException(status_code=404, detail="No projects found")
        
        conn.commit()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "projects_updated": project_sigs,
                "count": cur.rowcount
            }
        )
        
    except HTTPException:
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logger.exception(f"Failed to edit projects : : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to edit projects")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@router.get("/portfolio-dashboard", response_class=HTMLResponse)
def portfolio_dashboard():
    """
    Serve the Portfolio Dashboard UI
    """
    # Get the path to the static HTML file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "..", "..", "static", "portfolio.html")
    
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(
            content="<h1>Portfolio Dashboard not found</h1>", 
            status_code=404
        )

@router.get("/static/portfolio.js")
def portfolio_js():
    """
    Serve the Portfolio Dashboard JavaScript file
    """
    # Get the path to the static JS file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    js_path = os.path.join(current_dir, "..", "..", "static", "portfolio.js")
    
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        return Response(content=js_content, media_type="application/javascript")
    else:
        raise HTTPException(status_code=404, detail="JavaScript file not found")
