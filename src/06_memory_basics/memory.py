
memory = []

def write(event):
    memory.append(event)

def read():
    return memory

write({"event": "login"})
print(read())
