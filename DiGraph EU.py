import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# Load trade data from the Excel file
file_path = "/Users/kobevilleneuve/Desktop/Honors Project/EU Manual Export Data Entry.xlsx"
df_trade = pd.read_excel(file_path, sheet_name='2023')

# Extract exporter countries from the first column
exporters = df_trade.iloc[:, 0].tolist()

# Extract importer countries from the first row (excluding the first column)
importers = df_trade.columns[1:].tolist()

# Create a directed graph
G = nx.DiGraph()

# Add nodes (countries) to the graph
countries = set(exporters) | set(importers)
G.add_nodes_from(countries)

# Create a sink node to balance inflows and outflows
sink_node = "Global Balance"
G.add_node(sink_node)

total_inflows = 0
total_outflows = 0

# Add edges with weights (trade volumes) in both directions
for i, exporter in enumerate(exporters):
    row_sum = 0
    for j, importer in enumerate(importers):
        try:
            trade_value = df_trade.iloc[i, j + 1]
            if pd.notna(trade_value) and trade_value != "-":
                weight = float(trade_value)
                G.add_edge(exporter, importer, weight=weight, log_weight=np.log(weight + 1))
                row_sum += weight
        except IndexError:
            continue

    G.add_edge(exporter, sink_node, weight=row_sum, log_weight=np.log(row_sum + 1))
    total_outflows += row_sum

for j, importer in enumerate(importers):
    col_sum = 0
    for i, exporter in enumerate(exporters):
        try:
            trade_value = df_trade.iloc[i, j + 1]
            if pd.notna(trade_value) and trade_value != "-":
                col_sum += float(trade_value)
        except IndexError:
            continue

    G.add_edge(sink_node, importer, weight=col_sum, log_weight=np.log(col_sum + 1))
    total_inflows += col_sum

# Calculate eigenvector centrality (NumPy version, directed graph)
# --- Centrality Calculations ---
try:
    # Import-based eigenvector centrality (default: based on in-edges)
    eig_import = nx.eigenvector_centrality_numpy(G, weight='weight')

    # Export-based eigenvector centrality (reverse graph: based on out-edges)
    G_reversed = G.reverse(copy=True)
    eig_export = nx.eigenvector_centrality_numpy(G_reversed, weight='weight')

    # Print top 5 countries by each type (excluding sink)
    print("\nTop 9 Countries by Eigenvector Centrality (Imports - Influence as Destination):")
    for node, score in sorted(eig_import.items(), key=lambda x: -x[1]):
        if node != sink_node:
            print(f"{node}: {score:.4f}")

    print("\nTop 9 Countries by Eigenvector Centrality (Exports - Influence as Source):")
    for node, score in sorted(eig_export.items(), key=lambda x: -x[1]):
        if node != sink_node:
            print(f"{node}: {score:.4f}")

except nx.NetworkXException as e:
    print(f"Error computing eigenvector centrality: {e}")


# Define node positions
pos = nx.circular_layout(G)
pos[sink_node] = [0, -1.5]

# Extract edge widths
edge_widths = [d['log_weight'] for _, _, d in G.edges(data=True)]

# Draw the graph
plt.figure(figsize=(12, 12))
nx.draw(G, pos, with_labels=True, node_size=2500, node_color='lightblue', font_size=10,
        edge_color='gray', arrows=True, connectionstyle='arc3,rad=0.2', width=edge_widths)

# Inflow/outflow display
print(f"\nTotal inflows to sink node: {total_inflows:.2f}")
print(f"Total outflows from sink node: {total_outflows:.2f}")

plt.title("Directed Trade Network with Eigenvector Centrality & Log-Scaled Arrows")
plt.show()