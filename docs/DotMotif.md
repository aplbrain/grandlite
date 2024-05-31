# DotMotif

The [DotMotif](https://github.com/aplbrain/dotmotif) query language is a concise, declarative language for subgraph searches.

## Examples

### Interactively query a graph file downloaded from the internet with DotMotif

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

### Search motifs with DotMotif with a query argument, and post-process results with `jq`

> ```bash
> grandlite https://raw.githubusercontent.com/chengw07/NetWalk/master/data/karate.GraphML --language dotmotif -o jsonl --query 'A->B [weight>5]' | jq '.A'
> ```
