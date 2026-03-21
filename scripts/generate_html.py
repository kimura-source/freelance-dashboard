import json, re
from pathlib import Path


def main():
    d = json.loads(Path("data/data.json").read_text(encoding="utf-8"))
    updated = d.get("updatedDate", "")
    fs_js = json.dumps(d["fs"], ensure_ascii=False)
    idx = Path("index.html")
    if idx.exists():
        html = idx.read_text(encoding="utf-8")
        html = re.sub(r'const FS_RAW = \[.*?\];', f'const FS_RAW = {fs_js};', html, flags=re.DOTALL)
        html = re.sub(r'\d{4}年\d{1,2}月\d{1,2}日 \d{2}:\d{2}', updated, html)
    else:
        html = gen_simple(fs_js, updated)
    idx.write_text(html, encoding="utf-8")
    print(f"OK: {len(html):,} bytes")


def gen_simple(fs_js, updated):
    return (
        "<!DOCTYPE html><html lang=ja><head><meta charset=UTF-8>"
        "<title>フリーランスエージェント比較</title>"
        "<style>"
        "body{font-family:sans-serif;background:#f4f6f9;padding:20px}"
        "table{width:100%;border-collapse:collapse;background:#fff}"
        "th{background:#1d4ed8;color:#fff;padding:10px 12px;font-size:12px}"
        "td{padding:8px 12px;border-bottom:1px solid #f1f5f9;font-size:12px}"
        ".ok{color:#15803d;font-weight:600}.warn{color:#b91c1c;font-weight:600}"
        "</style></head><body>"
        "<h1>フリーランスエージェント比較</h1>"
        f"<p>更新：{updated}</p>"
        "<table><thead><tr><th>#</th><th>名前</th><th>募集中</th></tr></thead>"
        "<tbody id=tb></tbody></table>"
        "<script>"
        f"const D={fs_js};"
        "D.sort((a,b)=>b.open-a.open);"
        "D.forEach((r,i)=>{const t=document.createElement('tr');"
        "t.innerHTML=`<td>${i+1}</td><td>${r.n}</td>"
        "<td class=\"${r.open>0?'ok':'warn'}\">${r.open.toLocaleString()}</td>`;"
        "document.getElementById('tb').appendChild(t);});"
        "</script></body></html>"
    )


if __name__ == "__main__":
    main()
