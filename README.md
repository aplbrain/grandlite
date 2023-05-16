# grandlite

A SQLite-like tool for querying graphs from the command-line using graph query languages in in-memory Python.

Supports out-of-core graphs with [Grand](https://github.com/aplbrain/grand).

## Installation

```bash
$ pip install grandlite
```

## Usage

```bash
$ grandlite my-graph.graphml
>
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

## Command-line options

```
$ grandlite --help
usage: An interactive graph query tool for Cypher and other query languages.
       [-h] [-o {csv,json,jsonl}] [--query QUERY]
       [-l {cypher,dotmotif}]
       graph

positional arguments:
  graph                 The filename of the graph to load.

options:
  -h, --help            show this help message and exit
  -o {csv,json,jsonl}, --output {csv,json,jsonl}
                        The output format to use.
  --query QUERY         If not provided, enters an interactive prompt.
  -l {cypher,dotmotif}, --language {cypher,dotmotif}
                        The query language to use (default: cypher).
```

## Examples

#### Non-interactively query a GraphML file and output the results as JSON

```bash
$ grandlite my-graph.graphml --query 'match (a)-[]->(b) where a.type <> 1 return a,b limit 10' -o json
```

#### Interactively query a graph file downloaded from the internet, automatically inferring the file format

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

#### Interactively query a graph file downloaded from the internet with DotMotif

```
$ grandlite https://raw.githubusercontent.com/chengw07/NetWalk/master/data/karate.GraphML --language dotmotif

dotmotif> A -> B [weight>1]
          A.Faction != B.Faction

|    | A   | B   |
|---:|:----|:----|
|  0 | n0  | n8  |
|  1 | n0  | n31 |
|  2 | n1  | n30 |
|  3 | n2  | n8  |
|  4 | n2  | n27 |
|  5 | n2  | n28 |
|  6 | n2  | n32 |
|  7 | n8  | n0  |
|  8 | n8  | n2  |
|  9 | n13 | n33 |
| 10 | n27 | n2  |
| 11 | n28 | n2  |
| 12 | n30 | n1  |
| 13 | n31 | n0  |
| 14 | n32 | n2  |
| 15 | n33 | n13 |
```

#### Advanced Examples

> ##### Search motifs with DotMotif with a query argument, and post-process results with `jq`
>
> ```bash
> grandlite https://raw.githubusercontent.com/chengw07/NetWalk/master/data/karate.GraphML --language dotmotif -o jsonl --query 'A->B [weight>5]' | jq '.A'
> ```

---

<p align='center'><small>Made with 💙 at <a href='http://www.jhuapl.edu/'><img alt='JHU APL' align='center' src='https://user-images.githubusercontent.com/693511/62956859-a967ca00-bdc1-11e9-998e-3888e8a24e86.png' height='42px'></a></small></p>
