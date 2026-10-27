import sys, rdflib
from rdflib.namespace import RDF, RDFS, OWL
d=rdflib.Graph(); d.parse(sys.argv[1]); t=rdflib.Graph(); t.parse(sys.argv[2])
T="https://w3id.org/TTRpg#"
print("triples", len(d), len(t), "union", len(d+t), "overlap", len(d & t))
tdef=set(t.subjects(RDF.type,RDFS.Class))|set(t.subjects(RDF.type,RDF.Property))
used=set(u for tr in d for u in tr if isinstance(u,rdflib.URIRef) and str(u).startswith(T))
print("TTRpg terms DnD uses:", sorted(str(u)[len(T):] for u in used))
print("used but NOT defined in TTRpg:", sorted(str(u)[len(T):] for u in used-tdef))
print("TTRpg defined, unused by DnD:", sorted(str(u)[len(T):] for u in tdef-used))
for p in ["type","existsIn"]:
    u=rdflib.URIRef(T+p); print(p, [str(x) for x in t.objects(u,RDFS.domain)], [str(x) for x in t.objects(u,RDFS.range)])
print("non-std preds in TTRpg:", set(str(p) for p in t.predicates()))
# DnD-only roots that gain parents
ddef=set(d.subjects(RDF.type,RDFS.Class))
print("defined in both:", [str(x) for x in ddef & tdef])
for c in ["Weapon","Armor","Currency","Tools","Tool","ItemEnhancement","ItemType"]:
    u=rdflib.URIRef(T+c); print(c, "children in DnD:", len(list(d.subjects(RDFS.subClassOf,u))), "parents in TTRpg:", [str(x) for x in t.objects(u,RDFS.subClassOf)])
