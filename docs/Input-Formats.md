# Input Formats

Grandlite supports a growing variety of input formats. If your graph is in any of the formats below, it can be loaded directly using Grandlite (and [converted to any other supported format](Conversion.md) if you so choose).

## GraphML / GML / GPickle

Files can be read directly.

Under the hood, uses `networkx.read_graphml` etc.

## CSV

CSV edgelists can be read either with the assumption that the first two columns are source and target (and all remaining columns, if any, are edge attributes), or a header row can be specified.

### Without Header

With no header, the following URI formats for import can be used:

```bash
$ grandlite my-example-graph.csv
```

```bash
$ grandlite my-example-graph.edgelist
```

```bash
$ grandlite 'edgelist://my-example-graph.anyextension'
```

### CSV Edgelists with a Header Row

To read edgelist files with a header-row, you can specify the columns that correspond to source and target nodes. For example, in the following edgelist file,

```csv
MySource,MyTarget,Weight
1,2,0.5
2,3,0.7
```

you can specify the column names as follows:

```bash
$ grandlite 'h-edgelist(MySource:MyTarget):///path/to/my-example-graph.csv'
```

## OpenCypher

Vertex/Edge files in the OpenCypher import format can be read using the `vertex:` and `edge:` prefixes.

```bash
$ grandlite 'vertex:vertices.csv;edge:edges.csv'
```
