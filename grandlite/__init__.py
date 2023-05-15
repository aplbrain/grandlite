import pandas as pd
import pathlib
import sys
from prompt_toolkit import prompt
import networkx as nx
from grandcypher import GrandCypher


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


def prompt_loop():
    args = sys.argv
    host_graph_name = str(pathlib.Path(args[-1]).resolve())
    # Detect type of graph
    if host_graph_name.endswith(".gml") or host_graph_name.endswith(".gml.gz"):
        host_graph = nx.read_gml(host_graph_name)
    elif host_graph_name.endswith(".graphml") or host_graph_name.endswith(
        ".graphml.gz"
    ):
        host_graph = nx.read_graphml(host_graph_name)
    elif host_graph_name.endswith(".gpickle"):
        host_graph = nx.read_gpickle(host_graph_name)
    else:
        raise ValueError(f"Unknown graph file type for file '{host_graph_name}'.")
    prompt_loop_on_graph(host_graph)


if __name__ == "__main__":
    prompt_loop()
