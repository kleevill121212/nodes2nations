# nodes2nations
# EU Trade Network Centrality Project

This repository contains Python scripts and data supporting my honors project:  
"From Nodes to Nations: Centrality’s Impact on Economic Welfare"
Authored by *Kobe L. Villeneuve*, St. Lawrence University, May 2025.

# Overview
This project applies graph theory to analyze bilateral trade flows between top EU exporters from 2003 to 2023.  
It uses **eigenvector centrality** and other structural metrics to evaluate each country’s role in the trade network, and relates those measures to economic indicators such as GDP per capita, income inequality, and export diversification.

# Relevant Files
### `20-year visualization.py`
Generates an animated, dual-panel network graph using Plotly and NetworkX.  
Each frame represents one benchmark year (2003–2023) with import and export centrality visualized side-by-side.

### `DiGraph EU.py`
Constructs a static directed graph for the year 2023 with a sink node called Global Balance used for visual flow balance.  
This version is used to generate the final static image in the paper (Figure 6).

### `Non Digraph.py`
Creates an **undirected** version of the EU trade network and allows the user to set a trade volume threshold.  
This script recomputes centrality metrics on the filtered network and prints top-ranked countries interactively. It allows users to visualize the trade volume threshold by clicking through the interactive graphic. 

# Data
Manual bilateral trade data (export volume in USD) was retrieved from the  
[Observatory of Economic Complexity (OEC)](https://oec.world/en)  
and formatted into adjacency matrices for each year.

# Final Notes
Thank you for checking out my project :)
