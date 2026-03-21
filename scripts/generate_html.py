import json, re
from pathlib import Path

def js_val(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)

def agent_to_js(r):
    parts = [
        f'id:{r["id"]}',
        f'n:{json.dumps(r["n"], ensure_ascii=False)}',
        f'tot:{r["tot"]}',
        f'open:{r["open"]}',
        f'cl:{r["cl"]}',
    ]
    if "fhid" in r:
        parts.append(f'fhid:{js_val(r.get("fhid"))}')
    if r.get("exact"):
        parts.append("exact:true")
    return "{" + ",".join(parts) + "}"

def main():
    d = json.loads(Path("data/data.json").read_text(encoding="utf-8"))
    updated = d.get("updatedDate", "")
    fs_data = d.get("fs", [])
    fh_data = d.get("fh", [])

    # JS配列文字列を生成
    fs_js = "[\n" + ",\n".join("  " + agent_to_js(r) for r in fs_data) + "\n]"
    fh_js = "[\n" + ",\n".join("  " + agent_to_js(r) for r in fh_data) + "\n]"

    src = Path("dashboard.html")
    if not src.exists():
        print("ERROR: dashboard.html not found")
        return

    html = src.read_text(encoding="utf-8")

    # const FS=[...] を置換
    html = re.sub(
        r'const FS\s*=\s*\[.*?\];',
        f'const FS={fs_js};',
        html, flags=re.DOTALL
    )
    # const FH=[...] を置換
    html = re.sub(
        r'const FH\s*=\s*\[.*?\];',
        f'const FH={fh_js};',
        html, flags=re.DOTALL
    )
    # 更新日時を置換
    html = re.sub(
        r'エージェント調査 \d{4}-\d{2}',
        f'エージェント調査 {updated[:7]}',
        html
    )
    html = re.sub(
        r'📅 \d{4}年\d{1,2}月',
        f'📅 {updated[:7].replace("-", "年")}月',
        html
    )

    Path("index.html").write_text(html, encoding="utf-8")
    print(f"OK: dashboard updated, {len(html):,} bytes")

if __name__ == "__main__":
    main()
