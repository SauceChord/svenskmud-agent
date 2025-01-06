from openai import OpenAI
from ai_history import AIHistory
from ai_tools import AITools
import json

class AIAgent:
    def __init__(self, client : OpenAI, model, instruction, history = AIHistory(), tools : AITools = AITools()):
        self.client = client
        self.history = history
        self.model = model
        self.tools = tools
        self.instructions = []
        self.add_instruction(instruction)        

    def add_instruction(self, func):
        self.instructions.append(lambda : {'role': 'system', 'content': func()})

    async def respond_to(self, user_message : str) -> str:
        self.history.add_content('user', user_message)
        response = self.client.chat.completions.create(
            model = self.model,
            messages = [instr() for instr in self.instructions] + self.history.history,
            tools = self.tools.metadata if self.tools else None
        )
        message = response.choices[0].message

        if message:
            self.history.add(message)
        ai_message = message.content

        if message.tool_calls != None:
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = eval(tool_call.function.arguments)
                func_result = await self.tools.call(func_name, func_args)
                self.history.add_tool_call(tool_call.id, json.dumps({
                    "result": func_result
                }))
        
        return ai_message
