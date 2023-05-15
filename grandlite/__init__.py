import argparse
import pathlib
import sys

import networkx as nx
import pandas as pd
from grandcypher import GrandCypher
from prompt_toolkit import prompt


def detect_and_load_graph(graph_uri: str) -> nx.Graph:
    # Detect type of graph
    graph_path = str(pathlib.Path(graph_uri).absolute().resolve())
    if graph_path.endswith(".gml") or graph_path.endswith(".gml.gz"):
        host_graph = nx.read_gml(graph_path)  # type: ignore
    elif graph_path.endswith(".graphml") or graph_path.endswith(".graphml.gz"):
        host_graph = nx.read_graphml(graph_path)  # type: ignore
    elif graph_path.endswith(".gpickle"):
        host_graph = nx.read_gpickle(graph_path)  # type: ignore
    else:
        raise ValueError(f"Unknown graph file type for file '{graph_path}'.")
    return host_graph


def prompt_loop_on_graph(host_graph: nx.Graph):
    exiting = False
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

        # Parse the query using the GrandCypher parser
        results = GrandCypher(host_graph).run(text)
        # Print the results
        print(pd.DataFrame(results))


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
        "-c",
        "--cypher",
        help="A Cypher query to run.",
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
