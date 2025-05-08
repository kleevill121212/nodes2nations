import pandas as pd
import networkx as nx
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load the Excel file
file_path = "/Users/kobevilleneuve/Desktop/Honors Project/EU Manual Export Data Entry.xlsx"
excel_file = pd.ExcelFile(file_path)
sheet_names = excel_file.sheet_names


# Store all frames
combined_frames = []

for year in sorted(sheet_names):
    df_trade = pd.read_excel(file_path, sheet_name=year)
    exporters = df_trade.iloc[:, 0].tolist()
    importers = df_trade.columns[1:].tolist()

    G = nx.DiGraph()
    G.add_nodes_from(set(exporters) | set(importers))
  

    pos = nx.spring_layout(G, seed=42)
    pos.pop("Global Balance", None)

    for i, exporter in enumerate(exporters):
        row_sum = 0
        for j, importer in enumerate(importers):
            try:
                trade_value = df_trade.iloc[i, j + 1]
                if pd.notna(trade_value) and trade_value != "-":
                    weight = float(trade_value)
                    G.add_edge(exporter, importer, weight=weight)
                    row_sum += weight
            except IndexError:
                continue


    for j, importer in enumerate(importers):
        col_sum = 0
        for i, exporter in enumerate(exporters):
            try:
                trade_value = df_trade.iloc[i, j + 1]
                if pd.notna(trade_value) and trade_value != "-":
                    col_sum += float(trade_value)
            except IndexError:
                continue


    try:
        eig_import = nx.eigenvector_centrality_numpy(G, weight='weight')
        eig_export = nx.eigenvector_centrality_numpy(G.reverse(copy=True), weight='weight')
        eig_import.pop("Global Balance", None)
        eig_export.pop("Global Balance", None)
    except:
        eig_import = {node: 0 for node in G.nodes() if node != "Global Balance"}
        eig_export = eig_import.copy()

    def prepare_node_trace(eig_dict, col_offset, pos):
        node_x, node_y, node_size, node_color, node_text = [], [], [], [], []
        ranked_nodes = sorted(eig_dict.items(), key=lambda x: -x[1])
        top_names = [name for name, _ in ranked_nodes]

        for node in G.nodes():
            if node == "Global Balance":
                continue
            x, y = pos.get(node, (0, 0))
            x += col_offset
            node_x.append(x)
            node_y.append(y)
            score = eig_dict.get(node, 0)
            node_size.append(20 + 100 * score)
            node_text.append(f"{node}<br>Centrality: {score:.4f}")

            if node == top_names[0]:
                node_color.append("gold")
            elif node == top_names[1]:
                node_color.append("silver")
            elif node == top_names[2]:
                node_color.append("peru")
            elif node in top_names[3:5]:
                node_color.append("lightblue")
            elif node in top_names[5:9]:
                node_color.append("white")
            else:
                node_color.append("lightgray")

        return go.Scatter(
            x=node_x, y=node_y, mode='markers+text', text=node_text,
            hoverinfo='text',
            marker=dict(size=node_size, color=node_color, line_width=2),
            showlegend=False
        )

    def prepare_edge_trace(col_offset, pos):
        edge_x, edge_y = [], []
        for u, v in G.edges():
            if u in pos and v in pos:
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                edge_x += [x0 + col_offset, x1 + col_offset, None]
                edge_y += [y0, y1, None]
        return go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=1, color='gray'), hoverinfo='none')

    edge_trace_imp = prepare_edge_trace(-1, pos)
    edge_trace_exp = prepare_edge_trace(+1, pos)
    node_trace_imp = prepare_node_trace(eig_import, -1, pos)
    node_trace_exp = prepare_node_trace(eig_export, +1, pos)

    combined_frames.append(go.Frame(
        data=[edge_trace_imp, edge_trace_exp, node_trace_imp, node_trace_exp],
        name=year
    ))
    print(f"✅ Added frame for year: {year} | Nodes: {len(G.nodes())}, Edges: {len(G.edges())}")

# --- BUILD FIGURE ---
if not combined_frames:
    raise ValueError("No frames generated. Check Excel sheet formatting.")

fig = make_subplots(rows=1, cols=2, subplot_titles=("Import Centrality", "Export Centrality"))
fig.add_trace(combined_frames[0].data[0], row=1, col=1)
fig.add_trace(combined_frames[0].data[1], row=1, col=2)
fig.add_trace(combined_frames[0].data[2], row=1, col=1)
fig.add_trace(combined_frames[0].data[3], row=1, col=2)

# Dropdown
dropdown_buttons = [
    dict(label=frame.name,
         method="animate",
         args=[[frame.name], {"mode": "immediate",
                              "frame": {"duration": 0, "redraw": True},
                              "transition": {"duration": 0}}])
    for frame in combined_frames
]

fig.frames = combined_frames
fig.update_layout(
    title='EU Trade Network: Import vs Export Centrality (Color-coded by Rank)',
    showlegend=False,
    hovermode='closest',
    height=700,
   updatemenus=[
    dict(
        type="dropdown",
        showactive=True,
        buttons=dropdown_buttons,
        x=0.9,               # closer to right
        xanchor="right",     # anchor from right
        y=1.15,
        yanchor="top"
    )
],
    sliders=[],
    xaxis=dict(showticklabels=False, zeroline=False, showgrid=False),
    yaxis=dict(showticklabels=False, zeroline=False, showgrid=False),
    xaxis2=dict(showticklabels=False, zeroline=False, showgrid=False),
    yaxis2=dict(showticklabels=False, zeroline=False, showgrid=False),
    transition=dict(duration=0)
)

output_path = "/Users/kobevilleneuve/Desktop/Honors Project/EU_Trade_Centrality_Visualization.html"
fig.write_html(output_path, auto_play=False)
print(f"🎉 Visualization saved to {output_path}")
