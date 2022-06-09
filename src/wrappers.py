"""Wrapper classes."""


import enum
import json
from socket import socket


class Server:
    """Wrapper for a server connection."""

    def __init__(self):
        """Initialize the Server socket."""
        self.socket = socket()

    def connect(self):
        """Connect the socket to the local server."""
        try:
            self.socket.connect(("127.0.0.1", 5000))
        except Exception:
            return False

        return True

    def get_message(self):
        """Receives a message from the socket."""
        try:
            msg = self.socket.recv(2**12).decode()
        except Exception:
            return None

        return Message.decode(msg)

    def send_message(self, msg: str):
        """Send a message to the socket."""
        try:
            self.socket.send(msg.encode())
        except Exception:
            return


class Client:
    """Wrapper for a client connection."""

    def __init__(self, socket: socket):
        """Initialize the client."""
        self.socket = socket
        self.name = None

    def get_message(self):
        """Receives a message from the socket."""
        try:
            msg = self.socket.recv(2**12).decode()
        except Exception:
            return None

        return Message.decode(msg)

    def send_message(self, msg: str):
        """Send a message to the socket."""
        try:
            self.socket.send(msg.encode())
        except Exception:
            return

    def set_name(self, new_name: str):
        """Set a new name for the client."""
        self.name = new_name


class MessageType(enum.Enum):
    """Enum class to represent the message type."""

    JOIN = 0
    CHAT = 1
    NAME = 2
    QUIT = 3
    CAST = 4
    FAIL = 5


class Message:
    """Wrapper class for a message."""

    def __init__(self, msg_type: MessageType, author: str, msg_content: str):
        """Initialize a Message."""
        self.type = msg_type
        self.author = author
        self.content = msg_content

    def encode(self):
        """Encode a message as a json string."""
        encoding = json.dumps(
            {"type": self.type.value, "author": self.author, "content": self.content}
        )
        return encoding

    @classmethod
    def decode(cls, msg: str):
        """Decode a json string into a Message object."""
        message_json = json.loads(msg)

        msg_type: MessageType = MessageType(message_json.get("type"))
        msg_author: str = message_json.get("author")
        msg_content: str = message_json.get("content")

        return Message(msg_type, msg_author, msg_content)
