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
