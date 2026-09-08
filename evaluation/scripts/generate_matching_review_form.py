"""Generate a standalone browser form for matching review."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAIRS = ROOT / "evaluation" / "datasets" / "matching" / "pairs.jsonl"
OUTPUT = ROOT / "evaluation" / "reviews" / "matching-review.html"


def main() -> None:
    pairs = [json.loads(line) for line in PAIRS.read_text(encoding="utf-8").splitlines() if line.strip()]
    data = json.dumps([{"id": p["id"], "role": p["targetRole"], "resume": p["resumeText"], "jd": p["jdText"]} for p in pairs], ensure_ascii=False).replace("</", "<\\/")
    script = """const pairs=DATA;let index=0;
const key=()=>`matching-review-${reviewer.value}`;
const load=()=>JSON.parse(localStorage.getItem(key())||'{}');
function render(){const p=pairs[index],r=load()[p.id]||{};title.textContent=`${index+1}/${pairs.length} — ${p.id} (${p.role})`;resume.textContent=p.resume;jd.textContent=p.jd;score.value=r.score??'';notes.value=r.notes??'';progress.textContent=`Đã chấm ${Object.keys(load()).filter(id=>load()[id].score!==undefined).length}/${pairs.length}`;}
function persist(){const d=load(),p=pairs[index],n=Number(score.value);if(score.value!==''&&Number.isInteger(n)&&n>=0&&n<=100)d[p.id]={score:n,notes:notes.value};else delete d[p.id];localStorage.setItem(key(),JSON.stringify(d));}
function next(){persist();index=Math.min(index+1,pairs.length-1);render()} function previous(){persist();index=Math.max(index-1,0);render()}
reviewer.onchange=()=>{index=0;render()};score.onchange=persist;notes.onchange=persist;
function download(){persist();const d=load();if(Object.keys(d).length!==pairs.length){alert('Cần chấm đủ 70 pair trước khi tải CSV.');return}const rows=['pair_id,target_role,resume_text,job_description,score_0_to_100,reviewer_notes'];const q=v=>'"'+String(v??'').replaceAll('"','""')+'"';for(const p of pairs)rows.push([p.id,p.role,p.resume,p.jd,d[p.id].score,d[p.id].notes].map(q).join(','));const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([rows.join('\\n')],{type:'text/csv;charset=utf-8'}));a.download=`matching-${reviewer.value}.csv`;a.click()} render();""".replace("DATA", data)
    html = f'''<!doctype html><meta charset="utf-8"><title>Matching review</title><style>body{{font:16px system-ui;max-width:1000px;margin:32px auto;padding:0 16px}}textarea{{width:100%;height:150px}}button,input,select{{font:inherit;padding:8px}}.card{{background:#f5f7fa;padding:18px;margin:14px 0;border-radius:8px;white-space:pre-wrap}}</style><h1>CV–JD Matching review</h1><p>Chấm độc lập, không chia sẻ điểm với reviewer còn lại.</p><p>Reviewer <select id="reviewer"><option>reviewer-1</option><option>reviewer-2</option></select> <b id="progress"></b> <button onclick="previous()">← Trước</button> <button onclick="next()">Sau →</button> <button onclick="download()">Tải CSV</button></p><h2 id="title"></h2><div class="card"><b>CV</b><br><span id="resume"></span></div><div class="card"><b>JD</b><br><span id="jd"></span></div><label>Điểm 0–100 <input id="score" type="number" min="0" max="100" step="1"></label><p>Ghi chú<br><textarea id="notes"></textarea></p><script>{script}</script>'''
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
