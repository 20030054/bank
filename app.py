import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import tempfile

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

            for node in G.nodes():
                net.add_node(node, label=node)

            for source, target, data in G.edges(data=True):
                weight = data['weight']
                net.add_edge(source, target, value=weight, title=f"Amount: {weight}")

            # Render the graph
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
                net.show(tmp_file.name)
                st.write("### Transaction Network Graph")
                st.components.v1.html(tmp_file.read().decode("utf-8"), height=800, scrolling=True)

        else:
            st.error("The uploaded file does not have the required columns: Source_Branch, Target_Branch, Transaction_Amount")

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")