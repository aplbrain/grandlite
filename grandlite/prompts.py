import datetime
from typing import Any, Protocol

import networkx as nx
import pandas as pd
from dotmotif import GrandIsoExecutor, Motif
from grandcypher import GrandCypher
from prompt_toolkit import HTML

from .types import Response


class StatefulPrompt(Protocol):
    """
    A protocol that defines the interface for a stateful prompt.
    """

    def _get_state(self, graph_pointer: nx.Graph):
        """
        Retrieve the state associated with a graph pointer.
        """
        ...

    def _set_state(self, state):
        """
        Set the state associated with a graph pointer.
        """
        ...

    def prompt_text(self):
        """
        Return the prompt text.
        """
        ...

    def bottom_toolbar(self):
        ...

    def query(self, input_text: str) -> Any:
        """
        Perform a single query using the given input.
        """
        ...

    def submit_input(self, input_text: str) -> Response:
        """
        Submit the given input to the prompt.
        """
        ...

    def prompt_kwargs(self) -> dict:
        """
        Return any keyword arguments that should be passed to the prompt.
        """
        ...


class GrandCypherStatefulPrompt(StatefulPrompt):
    """
    A stateful prompt that uses Grand Cypher to query a graph using the Cypher
    query language.

    https://neo4j.com/docs/cypher-manual/current/

    """

    def __init__(self, graph_pointer: nx.Graph):
        """
        Initialize the prompt with a graph pointer.

        Arguments:
            graph_pointer: A NetworkX graph pointer.

        """
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

    def prompt_kwargs(self) -> dict:
        return {}

    def bottom_toolbar(self):
        return HTML(
            f"Language: <b>Cypher</b>    "
            f"Vertices: <b>{len(self._graph.nodes)}</b>    "
            f"Edges: <b>{len(self._graph.edges)}</b>    "
            + (
                f"Last results: <b>{len(self._last_results)}</b>"
                if self._last_results is not None
                else ""
            )
        )

    def query(self, input_text: str) -> Any:
        results = GrandCypher(self._graph).run(input_text)
        return pd.DataFrame(results)

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


class DotMotifStatefulPrompt(StatefulPrompt):
    """
    A stateful prompt that uses grandiso to query a graph using the DotMotif
    query language.

    https://github.com/aplbrain/dotmotif
    https://github.com/aplbrain/grandiso-networkx

    """

    def __init__(self, graph_pointer: nx.Graph):
        self._graph = graph_pointer
        self._last_results = None
        self._first_prompt = True

    def _get_state(self):
        return {
            "last_results": self._last_results,
            "first_prompt": self._first_prompt,
        }

    def _set_state(self, state):
        self._last_results = state.pop("last_results", None)
        self._first_prompt = state.pop("first_prompt", True)
        if len(state) > 0:
            raise ValueError(f"Unknown state keys: {list(state.keys())}")

    def prompt_text(self):
        return ("(esc+enter to submit)\n" if self._first_prompt else "") + "dotmotif> "

    def prompt_kwargs(self) -> dict:
        return {"multiline": True}

    def bottom_toolbar(self):
        return HTML(
            f"Language: <b>DotMotif</b>    "
            f"Vertices: <b>{len(self._graph.nodes)}</b>    "
            f"Edges: <b>{len(self._graph.edges)}</b>    "
            + (
                f"Last results: <b>{len(self._last_results)}</b>"
                if self._last_results is not None
                else ""
            )
        )

    def query(self, input_text: str) -> Any:
        results = GrandIsoExecutor(graph=self._graph).find(Motif(input_text))
        return pd.DataFrame(results)

    def submit_input(self, input_text: str) -> Response:
        self._first_prompt = False
        if input_text.lower().startswith("save"):
            # Choose the format from the filename provided:
            if self._last_results is None:
                return None, "No results to save."
            args = input_text.split(" ")[1:]
            if len(args) > 0:
                fmt = args[0].split(".")[-1]
                filename = args[0]
            else:
                fmt = "json"
                iso = datetime.datetime.now().isoformat()
                filename = f"results-{iso}.{fmt}"

            # Write the file:
            if fmt == "csv":
                self._last_results.to_csv(filename)
            elif fmt == "jsonl":
                self._last_results.to_json(filename, orient="records", lines=True)
            elif fmt == "json":
                self._last_results.to_json(filename, orient="records")
            elif fmt in ["md", "markdown"]:
                self._last_results.to_markdown(filename)
            elif fmt == "html":
                self._last_results.to_html(filename)
            else:
                return None, f"Unknown format: {fmt}"
            return f"Saved results to {filename}.", None

        try:
            results = GrandIsoExecutor(graph=self._graph).find(Motif(input_text))
            self._last_results = pd.DataFrame(results)
        except Exception as e:
            return None, str(e)
        return self._last_results.to_markdown(), None


# A mapping of query languages to their respective stateful prompts.
ALL_PROMPTS = {
    "cypher": GrandCypherStatefulPrompt,
    "dotmotif": DotMotifStatefulPrompt,
}


__all__ = ["ALL_PROMPTS", "GrandCypherStatefulPrompt", "DotMotifStatefulPrompt"]
