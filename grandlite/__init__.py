import argparse
import csv
import pathlib
import sys
import re
import tempfile

import networkx as nx
import requests
from prompt_toolkit import HTML, PromptSession, print_formatted_text
from grand_cypher_io import opencypher_buffers_to_graph

from .prompts import ALL_PROMPTS, StatefulPrompt

_opencypher_graphpath_regex = re.compile(r"vertex:(.*);edge:(.*)")

def _guess_delimiter(first_n_lines: list[str]) -> str:
    """
    Guess the delimiter of a CSV file from the first few lines.

    Arguments:
        first_n_lines: The first few lines of the CSV file.

    Returns:
        The guessed delimiter.

    """
    delimiters = [",", "\t", ";", "|"]
    # Return the first delimiter that appears in the first few lines and has
    # the same number of occurrences in each line.
    for delimiter in delimiters:
        # Appears at all?
        if not any(delimiter in line for line in first_n_lines):
            continue
        if all(line.count(delimiter) == first_n_lines[0].count(delimiter) for line in first_n_lines):
            return delimiter
    raise ValueError("Could not guess delimiter.")

def read_headered_edgelist(filename: str) -> nx.Graph:
    """
    Read a graph from a headered edgelist file.

    Arguments:
        filename: The name of the file to read.

    Returns:
        A NetworkX graph.

    """
    # The filename is of the form `h-edgelist(src:tgt)://{filename}`, so we
    # need to extract the the src column and tgt column from the filename,
    # and then read the file.
    match = re.match(r"h-edgelist\((.*):(.*)\)://(.*)", filename)
    if match is None:
        raise ValueError("Invalid headered edgelist file path.")
    src_col = match.group(1)
    tgt_col = match.group(2)
    filepath = match.group(3)
    # The file has a header row.
    # Use the CSV reader to read the file:
    def _without_srctgt(row):
        return {k: v for k, v in row.items() if k not in [src_col, tgt_col]}

    with open(filepath, "r") as f:
        delimiter = _guess_delimiter([next(f) for _ in range(5)])
    with open(filepath, "r") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        print(reader.fieldnames)
        edges = [(row[src_col], row[tgt_col], _without_srctgt(row)) for row in reader]
    return nx.DiGraph(edges)


def _infer_graph_filetype_from_contents(filename: str) -> str:
    """
    Infer the graph file type from the contents of the file.

    Arguments:
        filename: The name of the graph file.

    Returns:
        The file type, as a string.

    Raises:
        NotImplementedError: If the file type cannot be inferred.

    """
    # Make sure the file exists:
    if pathlib.Path(filename).exists():
        # If XML, assume GraphML
        first_chars = open(filename).read(500)
        if "<graphml" in first_chars:
            return "graphml"

        # If CSV, see if it's an edgelist:
        if "source,target" in first_chars:
            return "edgelist"

    # See if this is an OpenCypher collection of the form
    # `vertex:file,file,file;edge:file,file,file`:
    # Where `vertex` and `edge` are hardcoded, and `file` is a path to a file.
    # The files are assumed to be CSVs.
    match = _opencypher_graphpath_regex.match(filename)
    if match is not None:
        return "opencypher"


    raise NotImplementedError("Cannot infer graph file type from contents.")


def read_opencypher(paths: str) -> nx.Graph:
    """Read a graph from an OpenCypher CSV set of files.

    Arguments:
        path (str): A path of the form `_opencypher_graphpath_regex`.

    """
    parsed = _opencypher_graphpath_regex.match(paths)
    if parsed is None:
        raise ValueError("Invalid OpenCypher graph path.")
    # Parse the paths:
    vertex_paths = parsed.group(1).split(",")
    edge_paths = parsed.group(2).split(",")
    return opencypher_buffers_to_graph(vertex_paths, edge_paths)


def detect_and_load_graph(graph_uri: str) -> nx.Graph:
    """
    Read a graph from its URI and return a NetworkX.Graph-compatible API.

    Note that this API may be a true NetworkX.Graph, or it may be a Grand
    Graph, which proxies networkx library functions to other graph stores.

    Arguments:
        graph_uri: The URI of the graph.

    Returns:
        A NetworkX.Graph-compatible API.

    Raises:
        ValueError: If the graph file type is unknown.

    """

    if graph_uri.startswith("http://") or graph_uri.startswith("https://"):
        # Download to a temp file:
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(requests.get(graph_uri).content)
            f.flush()
            graph_uri = f.name

    # Detect type of graph file:
    # if pathlib.Path(graph_uri).exists():
    #     graph_path = str(pathlib.Path(graph_uri).absolute().resolve())
    # else:
    graph_path = graph_uri
    graph_type = None
    if graph_path.endswith(".gml") or graph_path.endswith(".gml.gz"):
        graph_type = "gml"
    elif graph_path.endswith(".graphml") or graph_path.endswith(".graphml.gz"):
        graph_type = "graphml"
    elif graph_path.endswith(".gpickle"):
        graph_type = "gpickle"
    elif graph_path.startswith("edgelist://"):
        graph_type = "edgelist"
    elif graph_path.startswith("h-edgelist("):
        graph_type = "edgelist-with-headers"

    if graph_type is None:
        graph_type = _infer_graph_filetype_from_contents(graph_path)

    readers = {
        "gml": nx.read_gml,  # type: ignore
        "graphml": nx.read_graphml,  # type: ignore
        "opencypher": read_opencypher,  # type: ignore
        "edgelist": nx.read_edgelist,  # type: ignore
        "edgelist-with-headers": read_headered_edgelist,  # type: ignore
    }
    if graph_type not in readers:
        raise ValueError(f"Unknown graph file type for file '{graph_path}'.")

    host_graph = readers[graph_type](graph_path)
    return host_graph


def prompt_loop_on_graph(host_graph: nx.Graph, query_language: str = "cypher"):
    """
    A prompt loop that allows the user to query a graph using a query language
    of their choice.

    Arguments:
        host_graph: The graph to query.
        query_language: The query language to use. Currently supported are
            'cypher' and 'dotmotif'.

    """
    session = PromptSession(enable_history_search=True)

    if query_language not in ALL_PROMPTS:
        raise ValueError(f"No known query parser for language '{query_language}'.")

    stateful_prompt: StatefulPrompt = ALL_PROMPTS[query_language](host_graph)

    exiting = False
    while not exiting:
        try:
            text = session.prompt(
                stateful_prompt.prompt_text(),
                **stateful_prompt.prompt_kwargs(),
                bottom_toolbar=stateful_prompt.bottom_toolbar(),
            )
        except KeyboardInterrupt:
            continue
        except EOFError:
            exiting = True
            continue

        if text.lower() in [
            "exit",
            "exit()",
            "quit",
            "quit()",
            "q",
        ]:
            exiting = True
            continue

        output, error = stateful_prompt.submit_input(text)
        if error is not None:
            print_formatted_text(
                HTML(f"<ansired>{error}</ansired>"),
            )
            continue
        if output is not None:
            print_formatted_text(
                HTML(f"<ansigreen>{output}</ansigreen>"),
            )


def cli():
    """
    The command-line interface for the tool.

    """
    argparser = argparse.ArgumentParser(
        "An interactive graph query tool for Cypher and other query languages.",
    )
    # One positional argument — the filename of the graph to load.
    argparser.add_argument(
        "graph",
        help="The filename of the graph to load.",
    )
    # Optional output formats; if none is provided, default to None.
    argparser.add_argument(
        "-o",
        "--output",
        choices=["csv", "json", "jsonl"],
        help="The output format to use.",
        default=None,
    )
    # Optional query parameter. If not provided, enters an interactive loop.
    argparser.add_argument(
        "-q",
        "--query",
        help="If not provided, enters an interactive prompt.",
        default=None,
    )
    argparser.add_argument(
        "-l",
        "--language",
        help="The query language to use (default: cypher).",
        choices=["cypher", "dotmotif"],
        default=None,
    )

    args = argparser.parse_args()
    host_graph = detect_and_load_graph(args.graph)
    language = args.language or "cypher"

    if args.query is not None:
        try:
            results = ALL_PROMPTS[language](host_graph).query(args.query)
        except Exception as e:
            print(e)
            sys.exit(1)
        results_formatter = {
            "csv": lambda x: x.to_csv(sys.stdout),
            "json": lambda x: x.to_json(sys.stdout, orient="records"),
            "jsonl": lambda x: x.to_json(sys.stdout, orient="records", lines=True),
        }
        if args.output is None:
            print(results)
        else:
            results_formatter[args.output](results)
    else:
        prompt_loop_on_graph(host_graph, language)


if __name__ == "__main__":
    cli()
