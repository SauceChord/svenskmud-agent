class AIHistory:
    def __init__(self, history = []):
        self.history = history

    def add_tool_call(self, tool_call_id, content):
        self.history.append({
            'role': 'tool',
            'content': content,
            'tool_call_id': tool_call_id
        })        

    def add_content(self, role, content):
        self.history.append({'role': role, 'content': content})

    def add(self, obj):
        self.history.append(obj)

    def prune(self):
        if len(self.history) > self.length:
            self.history = self.history[-self.length:]
