import sys, json, rdflib, collections
from rdflib.namespace import RDF, RDFS
g=rdflib.Graph(); g.parse(sys.argv[1], format="turtle")
D="https://w3id.org/DnD5eCharacter#"; T="https://w3id.org/TTRpg#"
def cur(u):
    u=str(u)
    if u.startswith(D): return "dnd:"+u[len(D):]
    if u.startswith(T): return "ttrpg:"+u[len(T):]
    if u.startswith("http://www.w3.org/2001/XMLSchema#"): return "xsd:"+u.split("#")[1]
    if u.startswith("http://www.w3.org/2002/07/owl#"): return "owl:"+u.split("#")[1]
    return u
nodes={}
def node(u):
    c=cur(u)
    if c not in nodes: nodes[c]={"id":c,"label":None,"comment":"","parents":[]}
    return nodes[c]
for s in g.subjects(RDF.type, RDFS.Class): node(s)
for s,o in g.subject_objects(RDFS.subClassOf):
    n=node(s); p=cur(o); node(o)
    if p not in n["parents"]: n["parents"].append(p)
for c,n in nodes.items():
    u=rdflib.URIRef(D+c[4:] if c.startswith("dnd:") else T+c[6:] if c.startswith("ttrpg:") else c)
    l=g.value(u,RDFS.label); cm=g.value(u,RDFS.comment)
    n["label"]=str(l) if l else c.split(":")[-1]
    n["comment"]=str(cm) if cm else ""
props=[]; pids=set()
for p in g.subjects(RDF.type, RDF.Property):
    pids.add(p)
    props.append({"id":cur(p),"label":str(g.value(p,RDFS.label) or ""),"comment":str(g.value(p,RDFS.comment) or ""),
      "domain":cur(g.value(p,RDFS.domain)),"range":cur(g.value(p,RDFS.range))})
rels=[]
for s,p,o in g:
    if p in pids and cur(s) in nodes:
        rels.append([cur(s),cur(p),cur(o) if isinstance(o,rdflib.URIRef) else str(o)])
for r in rels:
    if r[2] not in nodes and r[2].startswith(("dnd:","ttrpg:")): node(r[2]); print("missing target",r)
for pr in props:
    for k in ("domain","range"):
        if pr[k] not in nodes and not pr[k].startswith(("xsd","owl")): print("schema ref missing:",pr[k])
roots=[c for c,n in nodes.items() if not n["parents"]]
print("roots",roots)
multi=[(c,n["parents"]) for c,n in nodes.items() if len(n["parents"])>1]
print("multi",len(multi),multi[:15])
json.dump({"nodes":list(nodes.values()),"props":props,"rels":rels},open(sys.argv[2],"w",encoding="utf-8"),ensure_ascii=False,separators=(",",":"))
print(len(nodes),len(props),len(rels))
