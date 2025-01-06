import asyncio
import websockets
import telnetlib3
import os

class TelnetClient:
    def __init__(self):
        self.reader, self.writer = None, None

    async def connect(self, host, port):
        self.reader, self.writer = await telnetlib3.open_connection(host, port, encoding=False)

    async def read(self, size):
        return (await self.reader.read(size)).decode('latin1')

    async def readuntil(self, terminator):
        return (await self.reader.readuntil(terminator.encode('latin1'))).decode('latin1')

    async def readuntil_any(self, terminators=None):
        # If no terminators provided, read everything available
        if not terminators:
            return (await self.reader.read()).decode('latin1')
        
        buffer = ''
        while True:
            char = (await self.reader.read(1))
            if not char:  # Connection closed
                return buffer
            
            # Decode the character from bytes to string using latin1
            char = char.decode('latin1')
            buffer += char
            # Check if any terminator is found in the buffer
            for terminator in terminators:
                if terminator in buffer:
                    return buffer

    async def write(self, message: str):
        if message is not None:
            message = message + '\n'
            self.writer.write(message.encode('latin1'))

telnet_client = TelnetClient()
connected_clients = set()

async def echo(websocket):
    try:
        connected_clients.add(websocket)
        async for message in websocket:
            print(message)
            await telnet_client.write(message)
            
    finally:
        connected_clients.remove(websocket)

async def handle_telnet_connection():
    await telnet_client.connect('svenskmud.com', 2046)

    print(await telnet_client.readuntil('Vad heter du:'))
    await telnet_client.write(os.environ.get("SVENSKMUD_BOT_USERNAME") or input("Username: "))

    print(await telnet_client.readuntil('Lösenord:'))
    await telnet_client.write(os.environ.get("SVENSKMUD_BOT_PASSWORD") or input("Password: "))

    # Mer kommandon här, som t.ex. ta på kläder    
    while True:
        read_string = await telnet_client.read(1024*1024) # Eh, 1MB räcker nog?
        # Broadcast to all connected clients
        print(read_string)
        websockets.broadcast(connected_clients, read_string)

async def main():
    await asyncio.gather(
        websockets.serve(echo, "localhost", 40200),
        handle_telnet_connection(),
    )
    print("<Server closed>")

if __name__ == "__main__":
    asyncio.run(main())
