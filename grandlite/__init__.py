import argparse
import pathlib
import sys
import tempfile

import networkx as nx
import requests
from prompt_toolkit import HTML, PromptSession, print_formatted_text

from .prompts import ALL_PROMPTS, StatefulPrompt


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
    # If XML, assume GraphML
    first_100_chars = open(filename).read(500)
    if "<graphml" in first_100_chars:
        return "graphml"

    raise NotImplementedError("Cannot infer graph file type from contents.")


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
