# D&D 5e Ontology Explorer

Interactive views of the [DnD5eCharacter](https://w3id.org/DnD5eCharacter) ontology and the
[TTRpg](https://w3id.org/TTRpg) ontology it extends.

- **`docs/explorer.html`**: a 2D explorer with a collapsible class tree, a property schema graph and search.
- **`docs/3d.html`**: a 3D force graph of both ontologies merged. Dots are colored by the source file,
  and the page notes where the two files don't line up.

Open either file in a browser. They need internet access (for d3 / 3d-force-graph and fonts), and the 3D view needs WebGL.
If GitHub Pages is enabled on the `docs/` folder, `docs/index.html` links to both pages.

## Findings

These are problems found in the source files. Neither file has been changed.

| Issue | Where |
|---|---|
| `DnD5eCharacter:Divination` is both a magic school and a spell (one IRI). The same applies to `Shield` (armor and spell). | DnD5eCharacter.ttl lines 1843 / 2373, 1289 / 3417 |
| The alignment class is defined as `Alignemnt`, but the 9 alignments point to `Alignment`, which is never defined. | DnD5eCharacter.ttl |
| `DraconicAncestry` is used as a parent 9 times and never defined. | DnD5eCharacter.ttl |
| The D&D file uses `TTRpg:Tools` (123 children), but TTRpg defines `TTRpg:Tool`. | both |
| `TTRpg:ItemEnhancement` is used but defined in neither file. | DnD5eCharacter.ttl |
| `TTRpg:type` is declared three times with different domains and ranges. Under RDFS this means the intersection. | TTRpg.ttl lines 148–164 |
| A typo, `owl:invereOf`, drops the inverse between existsIn and hasItem. | TTRpg.ttl line 215 |

## Rebuilding

```sh
pip install rdflib
python scripts/build.py
```

`scripts/build.py` extracts the data from `ontology/*.ttl` (`extract.py`, `extract_merged.py`) and injects it into
`templates/*.html`, then writes the result to `docs/`. `merge_check.py` prints a summary of how the two files overlap.

## Credits and license

The ontologies in `ontology/` are by Ruben Wambacq (DnD5eCharacter, v1.0.6) and Ruben Wambacq and Robbe Van Herck (TTRpg).
They are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and included unmodified.
