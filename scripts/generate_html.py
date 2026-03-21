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
              # update date string pattern
              html = re.sub(r'\d{4}年\d{1,2}月\d{1,2}日 \d{2}:\d{2}', updated, html)
else:
          html = gen_simple(fs_js, updated)

    idx.write_text(html, encoding="utf-8")
    print(f"OK: index.html {len(html):,} bytes")

def gen_simple(fs_js, updated):
      return f"""<!DOCTYPE html>
      <html lang="ja"><head><meta charset="UTF-8">
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <title>フリーランスエージェント掲載比較ダッシュボード</title>
      <style>
      *{{margin:0;padding:0;box-sizing:border-box}}
      body{{font-family:sans-serif;background:#f4f6f9;padding:20px}}
      h1{{font-size:20px;margin-bottom:4px}}
      p{{color:#64748b;font-size:13px;margin-bottom:16px}}
      table{{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden}}
      th{{background:#1d4ed8;color:#fff;padding:10px 12px;text-align:left;font-size:12px}}
      td{{padding:8px 12px;border-bottom:1px solid #f1f5f9;font-size:12px}}
      .ok{{color:#15803d;font-weight:600}}
      .warn{{color:#b91c1c;font-weight:600}}
      </style></head><body>
      <h1>フリーランスエージェント掲載比較ダッシュボード</h1>
      <p>最終更新：{updated} | 毎朝8時自動更新</p>
      <table>
      <thead><tr><th>#</th><th>エージェント名</th><th>募集中件数</th><th>最終ページ</th></tr></thead>
      <tbody id="tb"></tbody>
      </table>
      <script>
      const FS_RAW = {fs_js};
      FS_RAW.sort((a,b)=>b.open-a.open);
      FS_RAW.forEach((r,i)=>{{
        const tr=document.createElement('tr');
          tr.innerHTML=`<td>${{i+1}}</td><td>${{r.n}}</td><td class="${{r.open>0?'ok':'warn'}}">${{r.open.toLocaleString()}}</td><td>${{r.lastPage||0}}</td>`;
            document.getElementById('tb').appendChild(tr);
            }});
            </script>
            </body></html>"""

if __name__ == "__main__":
      main()
