import telnetlib
import time
import os

# Connect to the MUD server
host = 'svenskmud.com'
port = 2046

class MUDClient:    
    def __init__(self, host, port):
        self.tn = telnetlib.Telnet(host, port)

    def send(self, command):
        self.tn.write(command.encode('iso-8859-1') + b'\n')

    def read(self, terminator):
        output = self.tn.read_until(terminator.encode('iso-8859-1'), timeout=5).decode('iso-8859-1')
        print(output)

    def read_some(self):
        output = self.tn.read_some().decode('iso-8859-1')
        if output:
            print(output)

    def authenticate(self):
        self.read("Vad heter du:")
        self.send(self.username())
        self.read("lösenord:")
        self.send(self.password())

    def username(self):
        return os.environ.get("SVENSKMUD_BOT_USERNAME") or input("Username: ")

    def password(self):
        return os.environ.get("SVENSKMUD_BOT_PASSWORD") or input("Password: ")

try:
    client = MUDClient(host, port)
    client.authenticate()

    while True:
        client.read("> ")
        # client.send(input())

except EOFError:
    print("Connection closed by the server.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    client.tn.close()