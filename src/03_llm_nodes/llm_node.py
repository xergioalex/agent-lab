
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

def call_llm(state):
    return {"response": llm.invoke(state["message"]).content}

print(call_llm({"message": "hello"}))
