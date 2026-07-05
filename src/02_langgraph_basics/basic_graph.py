
from langgraph.graph import StateGraph
from typing import TypedDict

class State(TypedDict):
    message: str

def a(state):
    return {"message": state["message"] + " -> A"}

def b(state):
    return {"message": state["message"] + " -> B"}

g = StateGraph(State)
g.add_node("A", a)
g.add_node("B", b)

g.set_entry_point("A")
g.add_edge("A", "B")
g.set_finish_point("B")

app = g.compile()
print(app.invoke({"message": "start"}))
