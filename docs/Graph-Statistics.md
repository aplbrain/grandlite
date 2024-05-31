# Graph Statistics

Grandlite can be used to compute graph statistics about a graph on disk, in a database, or in memory, by using the `--stats` flag.

You can optionally also pass a `-o/`/`--output` option. For a list of valid output formats, see [Output-Formats](Output-Formats).

## Examples

### Printing out statistics for a graph

```bash
$ grandlite example.graphml --stats
```

```
Nodes: 1123
Edges: 90811
Density: 0.07207187902279831
Orphans: 47
Leaves: 4
Max degree: 744
Max node: n841
Self-loops: 1123
```

### Printing out statistics for a graph in JSON format

```bash
$ grandlite example.graphml --stats -o json
```

```
{"Nodes": 1123, "Edges": 90811, "Density": 0.07207187902279831, "Orphans": 47, "Leaves": 4, "Max degree": 744, "Max node": "n841", "Self-loops": 1123}
```
