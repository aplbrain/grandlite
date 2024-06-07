# grandlite

A SQLite-like tool for querying graphs from the command-line using graph query languages in in-memory Python.

Supports out-of-core graphs with [Grand](https://github.com/aplbrain/grand).

## Installation

```bash
$ pip install grandlite
```

## Usage

### Get stats about a graph

```bash
$ poetry run grandlite --stats 'h-edgelist(pre:post)://white_1986_n2u.csv'
```

```
Nodes: 221
Edges: 1855
Density: 0.038153023447141096
Orphans: 0
Leaves: 7
Max degree: 44
Max node: RIMR
Self-loops: 52
```

### Run an interactive Cypher session

```bash
$ grandlite my-graph.graphml
```

```cypher
> match (a)-[]->(b) return a,b limit 3

        a       b
0  023620  364605
1  023620  438847
2  023620  462336

> save results.json

> exit()
```

Note that `save [filename]` will output `csv`, `json`, and `jsonl` files, depending on the extension provided; or will default to `results-XXXX.json` with XXX as a timestamp in ISO format, if no filename is provided.

For more information about saving, see [the docs](./docs/Saving).

## Command-line options

```
$ grandlite --help
usage: An interactive graph query tool for Cypher and other query languages.
       [-h]
       [-o {csv,json,jsonl}]
       [-q QUERY]
       [-l {cypher,dotmotif}]
       [--stats]
       [--convert OUTPUT_FILENAME]
       graph

positional arguments:
  graph                 The filename of the graph to load.

options:
  -h, --help            show this help message and exit
  -o {csv,json,jsonl}, --output {csv,json,jsonl}
                        The output format to use.
  -q QUERY, --query QUERY
                        If not provided, enters an interactive prompt.
  -l {cypher,dotmotif}, --language {cypher,dotmotif}
                        The query language to use (default: cypher).
  --stats               Print statistics about the graph and exit.
  --convert OUTPUT_FILENAME
                        Convert the graph to a new format, save to the
                        output filename specified, and exit.
```

## Input formats

Grandlite supports a growing variety of input formats. For a complete list, see [the docs](./docs/Input-Formats.d).

### Examples

#### OpenCypher

```bash
$ grandlite 'vertex:vertices.csv;edge:edges.csv'
```

#### CSV / Edgelist with or without headers

```bash
$ grandlite 'h-edgelist(pre:post)://white_1986_n2u.csv'
```

---

<p align='center'><small>Made with 💙 at <a href='http://www.jhuapl.edu/'><img alt='JHU APL' align='center' src='https://user-images.githubusercontent.com/693511/62956859-a967ca00-bdc1-11e9-998e-3888e8a24e86.png' height='42px'></a></small></p>

---
