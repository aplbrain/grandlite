import argparse
import datetime
import pathlib
import sys
import tempfile

import networkx as nx
import pandas as pd
import requests
from grandcypher import GrandCypher
from prompt_toolkit import PromptSession, print_formatted_text, HTML


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


_Output = _Error = str | None
Response = tuple[_Output, _Error]


class StatefulPrompt:
    def _get_state(self, graph_pointer: nx.Graph):
        raise NotImplementedError()

    def _set_state(self, state):
        raise NotImplementedError()

    def prompt_text(self):
        raise NotImplementedError()

    def submit_input(self, input_text: str) -> Response:
        raise NotImplementedError()


class GrandCypherStatefulPrompt(StatefulPrompt):
    def __init__(self, graph_pointer: nx.Graph):
        self._graph = graph_pointer
        self._last_results = None

    def _get_state(self):
        return {
            "last_results": self._last_results,
        }

    def _set_state(self, state):
        self._last_results = state.pop("last_results", None)
        if len(state) > 0:
            raise ValueError(f"Unknown state keys: {list(state.keys())}")

    def prompt_text(self):
        return "cypher> "

    def submit_input(self, input_text: str) -> Response:
        if input_text.lower().startswith("save"):
            if self._last_results is None:
                return None, "No results to save."
            args = input_text.split(" ")[1:]
            if len(args) > 0:
                format = args[0].split(".")[-1]
                filename = args[0]
            else:
                format = "json"
                iso = datetime.datetime.now().isoformat()
                filename = f"results-{iso}.{format}"

            if format == "csv":
                self._last_results.to_csv(filename)
            elif format == "jsonl":
                self._last_results.to_json(filename, orient="records", lines=True)
            elif format == "json":
                self._last_results.to_json(filename, orient="records")
            elif format in ["md", "markdown"]:
                self._last_results.to_markdown(filename)
            elif format == "html":
                self._last_results.to_html(filename)
            else:
                return None, f"Unknown format: {format}"
            return f"Saved results to {filename}.", None

        try:
            results = GrandCypher(self._graph).run(input_text)
            self._last_results = pd.DataFrame(results)
        except Exception as e:
            return None, str(e)
        return self._last_results.to_markdown(), None


def prompt_loop_on_graph(host_graph: nx.Graph, query_language: str = "cypher"):
    session = PromptSession(
        enable_history_search=True,
    )
    _prompts = {
        "cypher": GrandCypherStatefulPrompt,
    }
    if query_language not in _prompts:
        raise ValueError(f"No known query parser for language '{query_language}'.")

    stateful_prompt = _prompts[query_language](host_graph)

    exiting = False
    while not exiting:
        try:
            text = session.prompt(stateful_prompt.prompt_text())
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
