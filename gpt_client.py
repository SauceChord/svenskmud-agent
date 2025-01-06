import asyncio
import websockets

from openai import OpenAI
from ai_agent import AIAgent

import re

ansi_escape_pattern = re.compile(r'\x1B\[[0-?9;]*[mK]')

def strip_ansi_escape_sequences(text):
    clean_text = ansi_escape_pattern.sub('', text)
    return clean_text

def loadInstructions():
    with open('instructions.txt', 'r') as f:
        return f.read()

class MudAgent(AIAgent):
    def __init__(self, websocket, client : OpenAI, model, instructions):
        super().__init__(client, model, instructions)
        self.websocket = websocket
        self.emotional_states = {}
        self.add_instruction(self.get_emotional_states)
        self.tools.add(self.say)
        self.tools.add(self.go)
        self.tools.add(self.emotional_state)

    async def say(self, message):
        """Du säger <message>. En enkel rad som inte är för lång."""
        await self.command(f"säg {message}") 

    async def go(self, direction : str):
        """
        Du går <direction>. <direction> kan vara väster, öster, norr eller söder.
        Anropa endast om spelaren har bett dig att följa efter dem.
        """
        await self.command(direction)

    async def emotional_state(self, state : str, player : str):
        """Du är i känslomässigt tillstånd <state> till spelaren <player>."""
        print(f"I känslomässigt tillstånd {state} till spelaren {player}", flush=True)
        self.emotional_states[player] = state

    def get_emotional_states(self):
        emotion_list = "\n".join(f"Spelare {name} - {state}" for name, state in self.emotional_states.items())
        result = f"Du har följande känslomässiga tillstånd till spelare:\n{emotion_list}"
        return result

    async def command(self, command):
        print(command, flush=True)
        await self.websocket.send(command)    

async def listen():
    uri = "ws://localhost:40200"
    async with websockets.connect(uri) as websocket:
        client = OpenAI()
        agent = MudAgent(websocket, client, "gpt-4o-mini", loadInstructions)
        
        while True:
            response = await websocket.recv()
            print(response, flush=True)
            response = await agent.respond_to(strip_ansi_escape_sequences(response))

if __name__ == "__main__":
    asyncio.run(listen())