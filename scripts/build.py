"""Rebuild the two pages in docs/ from the .ttl files and the templates.

Usage (from the repo root):  python scripts/build.py
Needs rdflib (pip install rdflib).
"""
import json, pathlib, re, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
HEAD = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n')

def page(template, data_json, body_marker, out):
    html = (ROOT / "templates" / template).read_text(encoding="utf-8")
    html = html.replace("__DATA__", data_json.replace("</", "<\/"))
    head, body = html.split(body_marker, 1)
    (ROOT / "docs" / out).write_text(
        HEAD + head.rstrip() + "\n</head>\n<body>\n" + body_marker + body.rstrip() + "\n\n</body>\n</html>\n",
        encoding="utf-8")
    print("wrote docs/" + out)

def run(script, *args):
    subprocess.run([sys.executable, str(ROOT / "scripts" / script), *map(str, args)], check=True)

with tempfile.TemporaryDirectory() as tmp:
    dnd, ttrpg = ROOT / "ontology" / "DnD5eCharacter.ttl", ROOT / "ontology" / "TTRpg.ttl"
    run("extract.py", dnd, f"{tmp}/onto.json")
    run("extract_merged.py", dnd, ttrpg, f"{tmp}/onto_merged.json")
    onto = json.loads(pathlib.Path(f"{tmp}/onto.json").read_text(encoding="utf-8"))
    onto["version"] = re.search(r'DnD5eCharacter:version\s+"([^"]+)"', dnd.read_text(encoding="utf-8")).group(1)
    page("explorer.html", json.dumps(onto, ensure_ascii=False, separators=(",", ":")), '<div class="app">', "explorer.html")
    merged = pathlib.Path(f"{tmp}/onto_merged.json").read_text(encoding="utf-8")
    page("3d.html", merged, '<div class="wrap">', "3d.html")
    page("three.html", merged, '<div class="wrap">', "three.html")
