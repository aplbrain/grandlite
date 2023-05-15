import argparse
import datetime
import pathlib
import sys
import tempfile

import networkx as nx
import pandas as pd
import requests
from grandcypher import GrandCypher
from prompt_toolkit import prompt


def _infer_graph_filetype_from_contents(filename):
    # If XML, assume GraphML
    # If JSON, assume JSON Graph

    first_100_chars = open(filename).read(100)
    if "<graphml" in first_100_chars:
        return "graphml"

    raise NotImplementedError("Cannot infer graph file type from contents.")


def detect_and_load_graph(graph_uri: str) -> nx.Graph:
    """
    Read a graph from its URI and return a NetworkX.Graph-compatible API.

    Note that this API may be a true NetworkX.Graph, or it may be a Grand
    Graph, which proxies networkx library functions to other graph stores.

    """

    if graph_uri.startswith("http://") or graph_uri.startswith("https://"):
        # Download to a temp file:
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(requests.get(graph_uri).content)
            f.flush()
            graph_uri = f.name

    # Detect type of graph file:
    graph_path = str(pathlib.Path(graph_uri).absolute().resolve())
    graph_type = None
    if graph_path.endswith(".gml") or graph_path.endswith(".gml.gz"):
        graph_type = "gml"
    elif graph_path.endswith(".graphml") or graph_path.endswith(".graphml.gz"):
        graph_type = "graphml"
    elif graph_path.endswith(".gpickle"):
        graph_type = "gpickle"

    if graph_type is None:
        graph_type = _infer_graph_filetype_from_contents(graph_path)

    readers = {
        "gml": nx.read_gml,  # type: ignore
        "graphml": nx.read_graphml,  # type: ignore
    }
    if graph_type not in readers:
        raise ValueError(f"Unknown graph file type for file '{graph_path}'.")

    host_graph = readers[graph_type](graph_path)
    return host_graph


def prompt_loop_on_graph(host_graph: nx.Graph):
    exiting = False
    last_results = None
    while not exiting:
        try:
            text = prompt("> ")
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

        if text.lower().startswith("save"):
            if last_results is None:
                print("No results to save.")
                continue
            args = text.split(" ")[1:]
            if len(args) > 0:
                format = args[0].split(".")[-1]
                filename = args[0]
            else:
                format = "json"
                iso = datetime.datetime.now().isoformat()
                filename = f"results-{iso}.{format}"

            if format == "csv":
                last_results.to_csv(filename)
            elif format == "jsonl":
                last_results.to_json(filename, orient="records", lines=True)
            elif format == "json":
                last_results.to_json(filename, orient="records")

            continue

        # Parse the query using the GrandCypher parser
        try:
            results = pd.DataFrame(GrandCypher(host_graph).run(text))
            last_results = results
            # Print the results
            print(results)
        except Exception as e:
            print(f"Error: {e}")
            continue


def cli():
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
        "-qc",
        "--cypher",
        help="A Cypher query to run.",
        default=None,
    )
    argparser.add_argument(
        "-qd",
        "--dotmotif",
        help="A dotmotif query to run.",
        default=None,
    )

    args = argparser.parse_args()
    host_graph = detect_and_load_graph(args.graph)

    if args.cypher:
        try:
            results = GrandCypher(host_graph).run(args.cypher)
            results = pd.DataFrame(results)
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
        prompt_loop_on_graph(host_graph)


if __name__ == "__main__":
    cli()
