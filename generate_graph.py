import os
from app.graph.graph import interview_graph

os.makedirs("assets", exist_ok=True)

graph_image = interview_graph.get_graph().draw_mermaid_png()

with open("assets/graph.png", "wb") as f:
    f.write(graph_image)

print("Graph image saved to assets/graph.png")