
class State(dict):
    pass

def node_a(state):
    state["message"] += " | A"
    return state

def node_b(state):
    state["message"] += " | B"
    return state

state = {"message": "hello"}
state = node_a(state)
state = node_b(state)

print(state)
