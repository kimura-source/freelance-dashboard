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

    fs_js = "[\n" + ",\n".join("  " + agent_to_js(r) for r in fs_data) + "\n]"
    fh_js = "[\n" + ",\n".join("  " + agent_to_js(r) for r in fh_data) + "\n]"

    src = Path("dashboard.html")
    if not src.exists():
        print("ERROR: dashboard.html not found")
        return

    html = src.read_text(encoding="utf-8")

    # 置換前後の確認
    fs_match = re.search(r'const FS\s*=\s*\[', html)
    fh_match = re.search(r'const FH\s*=\s*\[', html)
    print(f"FS match: {bool(fs_match)}, FH match: {bool(fh_match)}")

    # const FS=[...]; を置換（改行・スペース対応）
    html, n1 = re.subn(
        r'const FS\s*=\s*\[[\s\S]*?\n\];',
        f'const FS={fs_js};',
        html
    )
    print(f"FS replaced: {n1} times")

    # const FH=[...]; を置換
    html, n2 = re.subn(
        r'const FH\s*=\s*\[[\s\S]*?\n\];',
        f'const FH={fh_js};',
        html
    )
    print(f"FH replaced: {n2} times")

    Path("index.html").write_text(html, encoding="utf-8")
    print(f"OK: {len(html):,} bytes, updated={updated}")

if __name__ == "__main__":
    main()
