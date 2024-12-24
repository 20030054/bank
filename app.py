import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import tempfile
import streamlit.components.v1 as components

# Streamlit app
st.title("Transaction Visualization among Branches")

# Upload file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Read Excel file
    try:
        df = pd.read_excel(uploaded_file)
        st.write("## Preview of the Data")
        st.dataframe(df.head())

        # Extract required columns (modify based on actual file structure)
        source_col = "Branch"  # Replace with actual source branch column name
        target_col = "Transaction To"  # Replace with actual target branch column name
        amount_col = "Credit"  # Replace with actual transaction amount column name

        if all(col in df.columns for col in [source_col, target_col, amount_col]):
            # Create graph
            G = nx.DiGraph()

            for _, row in df.iterrows():
                source = row[source_col]
                target = row[target_col]
                weight = row[amount_col]

                if G.has_edge(source, target):
                    G[source][target]['weight'] += weight
                else:
                    G.add_edge(source, target, weight=weight)

            # Visualize using pyvis
            net = Network(height="750px", width="100%", directed=True)

            # Set a physics layout to space nodes wider
            net.force_atlas_2based()

            for node in G.nodes():
                net.add_node(node, label=node)

            for source, target, data in G.edges(data=True):
                weight = data['weight']
                net.add_edge(source, target, value=weight, title=f"Amount: {weight}")

            # Allow node selection and dynamic coloring
            st.write("### Select a Node to Highlight")
            selected_node = st.text_input("Enter a node name to highlight (case-sensitive):")

            if selected_node and selected_node in G.nodes():
                for node in G.nodes():
                    color = "blue" if node == selected_node else "gray"
                    net.add_node(node, label=node, color=color)

                for source, target, data in G.edges(data=True):
                    weight = data['weight']
                    if source == selected_node:
                        edge_color = "green"
                    elif target == selected_node:
                        edge_color = "red"
                    else:
                        edge_color = "gray"
                    net.add_edge(source, target, value=weight, title=f"Amount: {weight}", color=edge_color)

            # Render the graph using pyvis
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
                    net.save_graph(tmp_file.name)  # Save the graph to an HTML file
                    tmp_file.seek(0)  # Move the pointer to the start
                    html_content = tmp_file.read().decode("utf-8")

                st.write("### Transaction Network Graph")
                components.html(html_content, height=800, scrolling=True)
            except Exception as e:
                st.error(f"An error occurred while rendering the graph: {e}")

        else:
            st.error("The uploaded file does not have the required columns: Source_Branch, Target_Branch, Transaction_Amount")

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
