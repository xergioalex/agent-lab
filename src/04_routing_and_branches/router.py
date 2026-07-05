
def router(state):
    if "block" in state["message"]:
        return {"intent": "blocker"}
    return {"intent": "general"}

print(router({"message": "we are blocked"}))
