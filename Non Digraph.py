import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Load trade data from the Excel file with the path to my folder
file_path = "/Users/kobevilleneuve/Desktop/Honors Project/EU Manual Export Data Entry.xlsx"
df_trade = pd.read_excel(file_path, sheet_name='2023')

# Identify countries
exporters = df_trade.iloc[:, 0].tolist()
importers = df_trade.columns[1:].tolist()
countries = set(exporters) | set(importers)

# Layout
pos = nx.circular_layout(list(countries))

# Setup figure
fig, ax = plt.subplots(figsize=(12, 12))

# Threshold setup
delta = 10
lambda_threshold = [10]

# Update function to draw graph and compute centralities
def update():
    ax.clear()
    G = nx.Graph()
    G.add_nodes_from(countries)

    for i, exporter in enumerate(exporters):
        for j, importer in enumerate(importers):
            try:
                export_value = df_trade.iloc[i, j + 1]
                import_value = df_trade.iloc[j, i + 1] if j < len(exporters) else 0

                export_value = float(export_value) if pd.notna(export_value) and export_value != "-" else 0
                import_value = float(import_value) if pd.notna(import_value) and import_value != "-" else 0

                total_volume = export_value + import_value

                if total_volume >= lambda_threshold[0]:
                    G.add_edge(exporter, importer, weight=total_volume, log_weight=np.log(total_volume + 1))

            except Exception:
                continue

    edge_widths = [d['log_weight'] for _, _, d in G.edges(data=True)]

    # Draw network
    nx.draw(G, pos, with_labels=True, node_size=2500, node_color='gray', font_size=10,
            edge_color='gray', width=edge_widths, ax=ax)
    ax.set_title(f"Combined Trade Network (Threshold: {lambda_threshold[0]} Billion)")
    ax.axis('off')
    fig.canvas.draw()

    # Compute centralities
    if G.number_of_edges() > 0:
        degree_centrality = nx.degree_centrality(G)
        eigenvector_centrality = nx.eigenvector_centrality_numpy(G)
        try:
            subgraph_centrality = nx.subgraph_centrality(G)
        except nx.NetworkXException as e:
            subgraph_centrality = {"Error": str(e)}

        print(f"\n[Threshold: {lambda_threshold[0]} Billion]")
        print("Top 5 Degree Centrality:")
        for node, score in sorted(degree_centrality.items(), key=lambda x: -x[1])[:5]:
            print(f"{node}: {score:.4f}")

        print("\nTop 5 Eigenvector Centrality (NumPy):")
        for node, score in sorted(eigenvector_centrality.items(), key=lambda x: -x[1])[:5]:
            print(f"{node}: {score:.4f}")

        print("\nTop 5 Subgraph Centrality:")
        if isinstance(subgraph_centrality, dict) and "Error" in subgraph_centrality:
            print(f"Subgraph Centrality Error: {subgraph_centrality['Error']}")
        else:
            for node, score in sorted(subgraph_centrality.items(), key=lambda x: -x[1])[:5]:
                print(f"{node}: {score:.4f}")
    else:
        print(f"\n[Threshold: {lambda_threshold[0]} Billion] No edges in the graph.")

# Click event handler
def on_click(event):
    lambda_threshold[0] += delta
    update()

# Bind click
fig.canvas.mpl_connect('button_press_event', on_click)

# Initial draw
update()
plt.show()