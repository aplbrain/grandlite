# Saving results

Results from Grandlite queries can be saved directly from the interactive shell by using the `save` keyword.

```
> match (a)-[]->(b) return a,b limit 3

        a       b
0  023620  364605
1  023620  438847
2  023620  462336

> save results.jsonl
```

Note that `save [filename]` will output `csv`, `json`, and `jsonl` files, depending on the extension provided; or will default to `results-XXXX.json` with XXX as a timestamp in ISO format, if no filename is provided.

The supported filenames for outputs are listed in [Output Formats](./Output-Formats.md).

Results are saved in record-orientation, meaning that the outputs will be a list of matches, each containing the query result entities. For the example above, `results.jsonl` will look like this:

```jsonl
{"a": "023620", "b": "364605"}
...
```
