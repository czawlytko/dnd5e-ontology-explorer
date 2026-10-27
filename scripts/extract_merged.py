"""Union two ontology files and record which file each class/statement came from."""
import sys, json, rdflib
from rdflib.namespace import RDF, RDFS, OWL
files = {"d": sys.argv[1], "t": sys.argv[2]}
G = {k: rdflib.Graph().parse(v, format="turtle") for k, v in files.items()}
U = G["d"] + G["t"]
PFX = [("https://w3id.org/DnD5eCharacter#", "dnd:"), ("https://w3id.org/TTRpg#", "ttrpg:"),
       ("http://xmlns.com/foaf/0.1/", "foaf:"), ("http://www.w3.org/2001/XMLSchema#", "xsd:"),
       ("http://www.w3.org/2002/07/owl#", "owl:"), ("http://www.w3.org/2000/01/rdf-schema#", "rdfs:")]
def cur(u):
    s = str(u)
    for full, p in PFX:
        if s.startswith(full): return p + s[len(full):]
    return s
def skip(c): return c.startswith(("xsd:", "owl:", "rdfs:"))
def src_of(triple):
    a = [k for k in G if triple in G[k]]
    return "".join(sorted(a))  # 'd', 't' or 'dt'
nodes = {}
def node(u):
    c = cur(u)
    if c not in nodes: nodes[c] = {"id": c, "uri": str(u), "parents": [], "src": ""}
    return nodes[c]
for k, g in G.items():
    for s in g.subjects(RDF.type, RDFS.Class):
        n = node(s)
        if k not in n["src"]: n["src"] += k
sub = []
for s, o in U.subject_objects(RDFS.subClassOf):
    n = node(s); node(o); p = cur(o)
    if p not in n["parents"]: n["parents"].append(p)
    sub.append([cur(s), p, src_of((s, RDFS.subClassOf, o))])
props = []
pids = set(U.subjects(RDF.type, RDF.Property))
for p in sorted(pids):
    doms = [cur(x) for x in U.objects(p, RDFS.domain)]; rngs = [cur(x) for x in U.objects(p, RDFS.range)]
    for x in list(U.objects(p, RDFS.domain)) + list(U.objects(p, RDFS.range)):
        if not skip(cur(x)): node(x)
    props.append({"id": cur(p), "label": str(U.value(p, RDFS.label) or ""),
                  "comments": sorted({str(c) for c in U.objects(p, RDFS.comment) if str(c)}),
                  "domains": doms, "ranges": rngs, "src": src_of((p, RDF.type, RDF.Property)),
                  "inverse": [cur(x) for x in U.objects(p, OWL.inverseOf)]})
rels = []
for s, p, o in U:
    if p in pids and isinstance(s, rdflib.URIRef) and cur(s) in nodes:
        if isinstance(o, rdflib.URIRef): node(o)
        rels.append([cur(s), cur(p), cur(o) if isinstance(o, rdflib.URIRef) else str(o), src_of((s, p, o))])
for c, n in nodes.items():
    u = rdflib.URIRef(n["uri"])
    l = U.value(u, RDFS.label); cm = U.value(u, RDFS.comment)
    n["label"] = str(l) if l else c.split(":")[-1]
    n["comment"] = str(cm) if cm else ""
    n["src"] = n["src"] or "x"
    del n["uri"]
meta = {"d": {"file": "DnD5eCharacter.ttl", "triples": len(G["d"])}, "t": {"file": "TTRpg.ttl", "triples": len(G["t"])},
        "union": len(U), "overlap": len(G["d"] & G["t"])}
json.dump({"nodes": list(nodes.values()), "sub": sub, "rels": rels, "props": props, "meta": meta},
          open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(meta, len(nodes), len(sub), len(rels), len(props))
print("undefined:", [c for c, n in nodes.items() if n["src"] == "x"])
print("from ttrpg:", sorted(c for c, n in nodes.items() if n["src"] == "t"))
print("sub src counts:", {k: sum(1 for x in sub if x[2] == k) for k in ("d", "t", "dt")})
