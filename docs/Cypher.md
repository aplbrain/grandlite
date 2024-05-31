# Cypher

Grandlite can be used to query graphs using the Cypher graph query language.

## Examples

### Run an interactive Cypher session

```bash
$ grandlite my-graph.graphml
```

```cypher
> match (a)-[]->(b) return a,b limit 10

        a       b
0  023620  364605
1  023620  438847
2  023620  462336
3  023620  962055
4  023620  314820
5  023620  755250
6  023620  001770
7  023620  055317
8  023620  419409
9  023620  482511

> save results.json

> exit()
```

Note that `save [filename]` will output `csv`, `json`, and `jsonl` files, depending on the extension provided; or will default to `results-XXXX.json` with XXX as a timestamp in ISO format, if no filename is provided.

### Non-interactively query a GraphML file and output the results as JSON

```bash
$ grandlite my-graph.graphml --query 'match (a)-[]->(b) where a.type <> 1 return a,b limit 10' -o json
```

### Interactively query a graph file downloaded from the internet, automatically inferring the file format

```bash
$ grandlite https://raw.githubusercontent.com/melaniewalsh/sample-social-network-datasets/master/sample-datasets/quakers/quakers-network.graphml

> match (a) return a, a.size
                   a  a.size
0       George Keith    10.0
1   William Bradford    10.0
2   George Whitehead    10.0
3         George Fox    10.0
4       William Penn    10.0
..               ...     ...
91      Joseph Besse    10.0
92     Samuel Bownas    10.0
93    Silvanus Bevan    10.0
94    John Penington    10.0
95      Lewis Morris    10.0
```
