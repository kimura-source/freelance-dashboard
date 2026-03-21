import json, re
from pathlib import Path

def js_val(v):
    if v is None: return "null"
    if isinstance(v, bool): return "true" if v else "false"
    return str(v)

def agent_to_js(r):
    parts = [f'id:{r["id"]}', f'n:{json.dumps(r["n"], ensure_ascii=False)}',
             f'tot:{r["tot"]}', f'open:{r["open"]}', f'cl:{r["cl"]}']
    if "fhid" in r: parts.append(f'fhid:{js_val(r.get("fhid"))}')
    if r.get("exact"): parts.append("exact:true")
    return "{" + ",".join(parts) + "}"

def parse_existing_js_array(html, var_name):
    """HTMLから既存のJS配列を解析して辞書で返す"""
    m = re.search(rf'const {var_name}\s*=\s*(\[[\s\S]*?\n\]);', html)
    if not m: return {}
    try:
        # JavaScriptオブジェクトをJSONに変換して解析
        js = m.group(1)
        js = re.sub(r'(\w+):', r'"\1":', js)      # キーをクォート
        js = re.sub(r':null', ':"__NULL__"', js)   # nullを一時変換
        js = re.sub(r':true', ':true', js)
        data = json.loads(js)
        result = {}
        for r in data:
            rid = r.get('"id"') or r.get('id')
            if rid: result[int(rid)] = r
        return result
    except Exception as e:
        print(f"parse error for {var_name}: {e}")
        return {}

def merge_fs(scraped, html):
    """スクレイプ結果をHTMLの既存データとマージ（0なら前回値保持）"""
    # 既存FS配列をパース
    m = re.search(r'const FS\s*=\s*\[([\s\S]*?)\n\];', html)
    existing = {}
    if m:
        for em in re.finditer(r'\{([^}]+)\}', m.group(1)):
            item = em.group(1)
            mid = re.search(r'id:(\d+)', item)
            mtot = re.search(r'tot:(\d+)', item)
            mopen = re.search(r'open:(\d+)', item)
            mcl = re.search(r'cl:(\d+)', item)
            if mid:
                existing[int(mid.group(1))] = {
                    'tot': int(mtot.group(1)) if mtot else 0,
                    'open': int(mopen.group(1)) if mopen else 0,
                    'cl': int(mcl.group(1)) if mcl else 0,
                }

    merged = []
    zero_count = sum(1 for r in scraped if r.get('tot', 0) == 0)
    all_zero = zero_count == len(scraped)
    print(f"FS scraped: {len(scraped)} agents, {zero_count} zeros, all_zero={all_zero}")

    for r in scraped:
        prev = existing.get(r['id'], {})
        # 全部0ならスクレイプ失敗 → 前回値を使う
        if all_zero and prev.get('tot', 0) > 0:
            r = dict(r)
            r['tot'] = prev['tot']
            r['open'] = prev['open']
            r['cl'] = prev['cl']
            print(f"  keeping prev for id={r['id']}: tot={r['tot']}")
        merged.append(r)
    return merged

def merge_fh(scraped, html):
    """FHも同様にマージ"""
    m = re.search(r'const FH\s*=\s*\[([\s\S]*?)\n\];', html)
    existing = {}
    if m:
        for em in re.finditer(r'\{([^}]+)\}', m.group(1)):
            item = em.group(1)
            mid = re.search(r'id:(\d+)', item)
            mtot = re.search(r'tot:(\d+)', item)
            mopen = re.search(r'open:(\d+)', item)
            if mid:
                existing[int(mid.group(1))] = {
                    'tot': int(mtot.group(1)) if mtot else 0,
                    'open': int(mopen.group(1)) if mopen else 0,
                }

    zero_count = sum(1 for r in scraped if r.get('tot', 0) == 0)
    all_zero = zero_count == len(scraped)
    print(f"FH scraped: {len(scraped)} agents, {zero_count} zeros, all_zero={all_zero}")

    merged = []
    for r in scraped:
        prev = existing.get(r['id'], {})
        if all_zero and prev.get('tot', 0) > 0:
            r = dict(r)
            r['tot'] = prev['tot']
            r['open'] = prev['open']
            print(f"  keeping prev for FH id={r['id']}: tot={r['tot']}")
        merged.append(r)
    return merged

def main():
    d = json.loads(Path("data/data.json").read_text(encoding="utf-8"))
    updated = d.get("updatedDate", "")
    fs_raw = d.get("fs", [])
    fh_raw = d.get("fh", [])

    src = Path("dashboard.html")
    if not src.exists():
        print("ERROR: dashboard.html not found"); return
    html = src.read_text(encoding="utf-8")

    # マージ（スクレイプ失敗時は前回値保持）
    fs_data = merge_fs(fs_raw, html)
    fh_data = merge_fh(fh_raw, html)

    fs_js = "[\n" + ",\n".join("  " + agent_to_js(r) for r in fs_data) + "\n]"
    fh_js = "[\n" + ",\n".join("  " + agent_to_js(r) for r in fh_data) + "\n]"

    html, n1 = re.subn(r'const FS\s*=\s*\[[\s\S]*?\n\];', f'const FS={fs_js};', html)
    html, n2 = re.subn(r'const FH\s*=\s*\[[\s\S]*?\n\];', f'const FH={fh_js};', html)
    print(f"FS replaced: {n1}, FH replaced: {n2}")

    
    # マージ済みデータをJSONに保存（Slack通知用）
    merged_out = dict(d)
    merged_out["fs"] = fs_data
    merged_out["fh"] = fh_data
    Path("data/data.json").write_text(
        __import__("json").dumps(merged_out, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    Path("index.html").write_text(html, encoding="utf-8")
    print(f"OK: {len(html):,} bytes, updated={updated}")

if __name__ == "__main__":
    main()
