
def planner(state):
    return {"plan": ["step1", "step2"]}

def executor(state):
    return {"result": "done"}

state = {}
state = planner(state)
state = executor(state)

print(state)
