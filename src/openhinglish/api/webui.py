"""Zero-dependency local test console for the OpenHinglish normalization engine.

Run it:
    python -m openhinglish.api.webui
then open http://127.0.0.1:8000 in your browser.

Uses only the Python standard library (http.server) — no FastAPI/Flask install needed.
"""
from __future__ import annotations

import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from openhinglish import normalize
from openhinglish.types import Config


def _result_to_dict(res) -> dict:
    return {
        "input": res.input,
        "display": res.display,
        "tts": res.tts,
        "confidence": res.confidence,
        "tokens": [
            {
                "surface": t.surface,
                "category": t.category.value,
                "display_form": t.display_form,
                "tts_form": t.tts_form,
                "confidence": round(t.confidence, 3),
                "alternatives": [
                    {
                        "category": a.category.value,
                        "display_form": a.display_form,
                        "tts_form": a.tts_form,
                        "score": round(a.score, 3),
                    }
                    for a in t.alternatives
                ],
                "trace": t.trace,
            }
            for t in res.tokens
        ],
    }


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OpenHinglish — Test Console</title>
<style>
  :root{
    --bg:#0d1117; --panel:#161b22; --panel2:#1c2330; --border:#2a3340;
    --txt:#e6edf3; --muted:#8b98a9; --accent:#5db0ff; --accent2:#7ee787;
    --warn:#f0b429; --bad:#ff7b72;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--txt);
    font-family:'Segoe UI',system-ui,'Noto Sans',sans-serif;line-height:1.5}
  .deva{font-family:'Nirmala UI','Noto Sans Devanagari','Mangal',serif}
  header{padding:22px 26px;border-bottom:1px solid var(--border);
    background:linear-gradient(180deg,#11161d,#0d1117)}
  header h1{margin:0;font-size:20px;letter-spacing:.3px}
  header h1 span{color:var(--accent)}
  header p{margin:6px 0 0;color:var(--muted);font-size:13px;max-width:760px}
  .wrap{max-width:980px;margin:0 auto;padding:24px 26px 60px}
  textarea{width:100%;min-height:88px;resize:vertical;background:var(--panel);
    color:var(--txt);border:1px solid var(--border);border-radius:10px;
    padding:14px 16px;font-size:18px;font-family:inherit}
  textarea:focus{outline:none;border-color:var(--accent)}
  .row{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:12px}
  button{background:var(--accent);color:#06121f;border:0;border-radius:9px;
    padding:11px 20px;font-size:15px;font-weight:600;cursor:pointer}
  button:hover{filter:brightness(1.08)}
  .toggle{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:14px}
  select{background:var(--panel);color:var(--txt);border:1px solid var(--border);
    border-radius:7px;padding:7px 10px;font-size:14px}
  .chips{margin-top:14px;display:flex;gap:8px;flex-wrap:wrap}
  .chip{background:var(--panel2);border:1px solid var(--border);color:var(--muted);
    border-radius:20px;padding:6px 13px;font-size:13px;cursor:pointer}
  .chip:hover{border-color:var(--accent);color:var(--txt)}
  .out{margin-top:26px;display:none}
  .cards{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  @media(max-width:720px){.cards{grid-template-columns:1fr}}
  .card{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:16px 18px}
  .card .lbl{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.6px}
  .card .val{font-size:26px;margin-top:8px;word-break:break-word}
  .conf{margin-top:16px;color:var(--muted);font-size:13px}
  .bar{height:8px;background:var(--panel2);border-radius:6px;overflow:hidden;margin-top:6px}
  .bar > i{display:block;height:100%;background:linear-gradient(90deg,var(--bad),var(--warn),var(--accent2))}
  h3{margin:28px 0 10px;font-size:15px;color:var(--muted);font-weight:600}
  table{width:100%;border-collapse:collapse;font-size:14px}
  th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--border);vertical-align:top}
  th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.5px}
  .badge{display:inline-block;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:.3px}
  .b-HINDI_ROMAN,.b-HINDI_DEVA{background:#16331f;color:var(--accent2)}
  .b-ENGLISH{background:#10263d;color:var(--accent)}
  .b-NAME{background:#321d3a;color:#d2a8ff}
  .b-BRAND{background:#3a2a12;color:var(--warn)}
  .b-NUMBER,.b-TIME,.b-DATE{background:#0f2f33;color:#56d4dd}
  .b-ACRONYM{background:#2d2540;color:#c9b3ff}
  .b-UNKNOWN{background:#3a1d1d;color:var(--bad)}
  .b-PUNCT,.b-EMOJI,.b-URL{background:#222a35;color:var(--muted)}
  .mono{font-family:'Cascadia Code',Consolas,monospace;font-size:12px;color:var(--muted)}
  .alts{color:var(--muted);font-size:12px}
  details summary{cursor:pointer;color:var(--accent);font-size:12px}
  details ul{margin:6px 0 0;padding-left:16px}
  details li{font-size:12px;color:var(--muted);font-family:'Cascadia Code',Consolas,monospace}
  .err{color:var(--bad);margin-top:16px}
  .note{background:#21170a;border:1px solid #4a3613;color:#f0c674;border-radius:9px;
    padding:10px 14px;font-size:13px;margin-top:18px}
</style>
</head>
<body>
<header>
  <h1><span>Open</span>Hinglish — Test Console <span style="font-size:12px;color:var(--muted)">V0.1</span></h1>
  <p>Type Roman-Hinglish and see how the engine normalizes it. <b>display</b> = human-readable
  (English/brands stay Latin); <b>tts</b> = fully resolved for a Devanagari TTS. Word order is
  preserved — the engine does not reorder grammar or insert punctuation (V1 scope).</p>
</header>

<div class="wrap">
  <textarea id="inp" placeholder="e.g. bhai kal mera intv h paytm me">bhai kal mera intv h paytm me</textarea>
  <div class="row">
    <button id="go">Normalize</button>
    <div class="toggle">Numbers in
      <select id="lang">
        <option value="hindi">Hindi (चार)</option>
        <option value="english">English (four)</option>
      </select>
    </div>
  </div>
  <div class="chips" id="chips"></div>

  <div class="note">Heads-up: V0.1 ships tiny <b>seed</b> lexicons (~13 Hindi words, 4 names, 4 brands).
  Words outside the seed show as <span class="badge b-UNKNOWN">UNKNOWN</span> or use a rough
  akshara fallback. The per-token <b>trace</b> tells you exactly what fired.</div>

  <div class="out" id="out">
    <div class="cards">
      <div class="card"><div class="lbl">display</div><div class="val deva" id="display"></div></div>
      <div class="card"><div class="lbl">tts</div><div class="val deva" id="tts"></div></div>
    </div>
    <div class="conf">overall confidence: <b id="confval"></b>
      <div class="bar"><i id="confbar"></i></div>
    </div>
    <h3>Per-token breakdown</h3>
    <table>
      <thead><tr><th>surface</th><th>category</th><th>display</th><th>tts</th>
        <th>conf</th><th>alternatives</th><th>trace</th></tr></thead>
      <tbody id="rows"></tbody>
    </table>
  </div>
  <div class="err" id="err"></div>
</div>

<script>
const EXAMPLES = [
  "bhai kal mera intv h paytm me",
  "kal mera meeting hai office me",
  "shankar mishra ka interview RBI me hai",
  "aaj zomato se 4 order aaye",
  "paytm pe 100 rupaye bheje",
  "intervew h kal"
];
const chips = document.getElementById('chips');
EXAMPLES.forEach(e=>{
  const c=document.createElement('span'); c.className='chip'; c.textContent=e;
  c.onclick=()=>{document.getElementById('inp').value=e; run();};
  chips.appendChild(c);
});

function esc(s){return (s||'').replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));}

async function run(){
  const text=document.getElementById('inp').value;
  const lang=document.getElementById('lang').value;
  const err=document.getElementById('err'); err.textContent='';
  try{
    const r=await fetch('/normalize',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({text,number_words_lang:lang})});
    if(!r.ok){err.textContent='Server error '+r.status; return;}
    const d=await r.json();
    document.getElementById('out').style.display='block';
    document.getElementById('display').textContent=d.display;
    document.getElementById('tts').textContent=d.tts;
    const pct=Math.round((d.confidence||0)*100);
    document.getElementById('confval').textContent=pct+'%';
    document.getElementById('confbar').style.width=pct+'%';
    const rows=document.getElementById('rows'); rows.innerHTML='';
    d.tokens.forEach(t=>{
      const alts=(t.alternatives||[]).map(a=>esc(a.display_form)+' <span class=mono>('+a.category+' '+a.score+')</span>').join('<br>')||'<span class=mono>—</span>';
      const trace='<details><summary>'+t.trace.length+' steps</summary><ul>'+t.trace.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul></details>';
      rows.insertAdjacentHTML('beforeend',
        '<tr><td class=mono>'+esc(t.surface)+'</td>'+
        '<td><span class="badge b-'+t.category+'">'+t.category+'</span></td>'+
        '<td class=deva>'+esc(t.display_form)+'</td>'+
        '<td class=deva>'+esc(t.tts_form)+'</td>'+
        '<td>'+t.confidence+'</td>'+
        '<td class=alts>'+alts+'</td>'+
        '<td>'+trace+'</td></tr>');
    });
  }catch(e){err.textContent='Could not reach server: '+e;}
}
document.getElementById('go').onclick=run;
document.getElementById('inp').addEventListener('keydown',e=>{
  if((e.ctrlKey||e.metaKey)&&e.key==='Enter') run();
});
run();
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, ctype: str, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            self._send(200, "text/html; charset=utf-8", PAGE.encode("utf-8"))
        else:
            self._send(404, "text/plain; charset=utf-8", b"not found")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/normalize":
            self._send(404, "text/plain; charset=utf-8", b"not found")
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
            text = payload.get("text", "")
            lang = payload.get("number_words_lang", "hindi")
            res = normalize(text, Config(number_words_lang=lang))
            body = json.dumps(_result_to_dict(res), ensure_ascii=False).encode("utf-8")
            self._send(200, "application/json; charset=utf-8", body)
        except Exception as exc:  # keep the console resilient
            body = json.dumps({"error": str(exc)}).encode("utf-8")
            self._send(500, "application/json; charset=utf-8", body)

    def log_message(self, *args) -> None:  # silence per-request logging
        return


def main(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True) -> None:
    url = f"http://{host}:{port}"
    print(f"OpenHinglish test console running at {url}  (Ctrl+C to stop)")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
