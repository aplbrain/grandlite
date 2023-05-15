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

> exit()
```

## Command-line options

```bash
$ grandlite --help
usage: An interactive graph query tool for Cypher and other query languages.
       [-h] [-o {csv,json,jsonl}] [-c CYPHER] graph

positional arguments:
  graph                 The filename of the graph to load.

options:
  -h, --help            show this help message and exit
  -o {csv,json,jsonl}, --output {csv,json,jsonl}
                        The output format to use.
  -c CYPHER, --cypher CYPHER
                        A Cypher query to run.
```

## Examples

#### Non-interactively query a GraphML file and output the results as JSON

```bash
grandlite my-graph.graphml -c 'match (a)-[]->(b) where a.type <> 1 return a,b limit 10' --json
```
