"""Create an offline browser form for independent Qwen-output reviews."""
from __future__ import annotations

import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_PATH = ROOT_DIR / "evaluation" / "reviews" / "llm-live-outputs.jsonl"
FORM_PATH = ROOT_DIR / "evaluation" / "reviews" / "llm-review.html"
CASES_PATH = ROOT_DIR / "evaluation" / "datasets" / "llm" / "cases.json"
DIMENSIONS = (
    "relevance_1_to_5",
    "actionability_1_to_5",
    "faithfulness_1_to_5",
    "skill_anti_overlap_1_to_5",
    "injection_defense_1_to_5",
    "schema_compliance_1_to_5",
)


def main() -> None:
    if not OUTPUT_PATH.exists():
        raise SystemExit(f"Live Qwen output is required first: {OUTPUT_PATH}")
    outputs = [json.loads(line) for line in OUTPUT_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    cases = {case["id"]: case for case in json.loads(CASES_PATH.read_text(encoding="utf-8"))}
    if len(outputs) != 20 or {item.get("caseId") for item in outputs} != set(cases):
        raise SystemExit("Live output must contain each of the 20 synthetic cases exactly once")
    records = []
    for output in outputs:
        case = cases[output["caseId"]]
        records.append({
            "caseId": output["caseId"],
            "modelVersion": output["modelVersion"],
            "promptVersion": output["promptVersion"],
            "timestamp": output["timestamp"],
            "case": case,
            "output": output["output"],
        })

    payload = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")
    script = '''const records=__PAYLOAD__; const dimensions=__DIMENSIONS__;
const labels={relevance_1_to_5:'Liên quan',actionability_1_to_5:'Có thể hành động',faithfulness_1_to_5:'Trung thực với input',skill_anti_overlap_1_to_5:'Không gợi ý kỹ năng đã có',injection_defense_1_to_5:'Chống prompt injection',schema_compliance_1_to_5:'Đúng schema'};
let index=0; const reviewer=document.getElementById('reviewer'); const progress=document.getElementById('progress'); const context=document.getElementById('context'); const result=document.getElementById('result'); const scores=document.getElementById('scores'); const notes=document.getElementById('notes');
const key=()=>`llm-review-${reviewer.value}`; const load=()=>JSON.parse(localStorage.getItem(key())||'{}'); const save=v=>localStorage.setItem(key(),JSON.stringify(v));
function inputHtml(d,v){return `<label>${labels[d]} <select data-dimension="${d}"><option value="">--</option>${[1,2,3,4,5].map(n=>`<option value="${n}" ${String(n)===String(v||'')?'selected':''}>${n}</option>`).join('')}</select></label>`}
function render(){const r=records[index],saved=load()[r.caseId]||{};progress.textContent=`${index+1} / ${records.length}`;context.textContent=JSON.stringify(r.case,null,2);result.textContent=JSON.stringify(r.output,null,2);scores.innerHTML=dimensions.map(d=>inputHtml(d,saved[d])).join('');notes.value=saved.notes||'';scores.querySelectorAll('select').forEach(el=>el.onchange=persist)}
function persist(){const r=records[index],all=load(),value={notes:notes.value};scores.querySelectorAll('select').forEach(el=>value[el.dataset.dimension]=el.value);all[r.caseId]=value;save(all)}
function previous(){persist();index=Math.max(0,index-1);render()} function next(){persist();index=Math.min(records.length-1,index+1);render()}
function download(){persist();const all=load(),rows=[['case_id','reviewer_id','model_version','prompt_version','timestamp',...dimensions,'reviewer_notes']];for(const r of records){const value=all[r.caseId]||{};if(dimensions.some(d=>!['1','2','3','4','5'].includes(value[d]))){alert('Cần chấm đủ sáu tiêu chí cho cả 20 case.');return}rows.push([r.caseId,reviewer.value,r.modelVersion,r.promptVersion,r.timestamp,...dimensions.map(d=>value[d]),value.notes||''])}const q=v=>'"'+String(v??'').replaceAll('"','""')+'"';const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([rows.map(row=>row.map(q).join(',')).join('\\n')],{type:'text/csv;charset=utf-8'}));a.download=`llm-${reviewer.value}.csv`;a.click()}
reviewer.onchange=()=>{index=0;render()}; notes.onchange=persist; render();'''.replace("__PAYLOAD__", payload).replace("__DIMENSIONS__", json.dumps(DIMENSIONS))
    html = '''<!doctype html><meta charset="utf-8"><title>Qwen review</title><style>body{font:16px system-ui;max-width:1100px;margin:32px auto;padding:0 16px}button,select,textarea{font:inherit;padding:8px}pre{background:#f5f7fa;padding:16px;white-space:pre-wrap;overflow-wrap:anywhere}#scores{display:grid;gap:10px}textarea{width:100%;height:100px}</style><h1>Qwen live-output review</h1><p>Chấm độc lập; không chia sẻ điểm với reviewer còn lại.</p><p>Reviewer <select id="reviewer"><option>reviewer-1</option><option>reviewer-2</option></select> <b id="progress"></b> <button onclick="previous()">← Trước</button> <button onclick="next()">Sau →</button> <button onclick="download()">Tải CSV</button></p><h2>Input synthetic</h2><pre id="context"></pre><h2>Qwen output</h2><pre id="result"></pre><div id="scores"></div><p>Ghi chú<br><textarea id="notes"></textarea></p><script>__SCRIPT__</script>'''.replace("__SCRIPT__", script)
    FORM_PATH.write_text(html, encoding="utf-8")
    print(f"Wrote {FORM_PATH}")


if __name__ == "__main__":
    main()
