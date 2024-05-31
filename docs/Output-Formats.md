# Output Formats

Grandlite supports a variety of output formats. These are:

-   **`json`**: A JSON-compatible format that can be passed directly into tools like `jq`.
-   **`jsonl`**: The [JSON-Lines](https://jsonlines.org/) format (one JSON document per line)
-   **`csv`**: A comma-separated output, starting with a header line. Values containing commas are wrapped in quotes.

These formats are also valid for the `--stats` flag (see [Graph Statistics](Graph-Statistics.md)
