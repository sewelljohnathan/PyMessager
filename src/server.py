"""Server side of this application."""

from socket import socket
from threading import Thread

from colorama import Fore, Style

from wrappers import Client, Message, MessageType

# Global variables
show_actions = True


def main():
    """Set up clients and threads."""
    # Set up the server socket
    clients: set[Client] = set()
    server_socket = socket()
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen()

    # Create Thread to listen for clients
    listener_thread = Thread(target=client_listener, args=(clients, server_socket))
    listener_thread.daemon = True
    listener_thread.start()

    # Listen for command to close the server
    print("Type a command or 'h' for help")
    while True:

        user_input = input().lower()

        # Print the self-assigned names of all connected clients
        if user_input == "names":
            for c in clients:
                print(c.name)

        # Shut down the server
        elif user_input == "q" or user_input == "quit":
            break

        elif user_input == "s" or user_input == "show-actions":
            global show_actions
            show_actions = not show_actions

        # Show a help message
        elif user_input == "h" or user_input == "help":
            print_help()

        # Send a message to all clients from the server
        else:
            msg = Message(MessageType.CAST, "", user_input)
            forward_message(clients, None, msg)


def print_help():
    """Print cli options."""
    print("Server Command Help")
    print("\"names\" - Print the names of all connected clients.")
    print("\"show-actions\" or \"s\" - Toggles printing of action logs.")
    print("\"quit\" or \"q\" - Shut down the server.")
    print("\"help\" or \"h\" - Show this message.")
    print(
        "[any other message] - Sends the text to all clients as a server broadcast message."
    )


def client_listener(clients: set[Client], server_socket: socket):
    """Receive new socket connections."""
    # Infinite loop for listening
    while True:

        # Get the socket connection
        client_socket, client_address = server_socket.accept()
        new_client = Client(client_socket)

        # Create Thread to listen for incoming messages
        new_thread = Thread(
            target=client_receiver,
            args=(
                clients,
                new_client,
            ),
        )
        new_thread.daemon = True
        new_thread.start()


def client_receiver(clients: set[Client], client: Client):
    """Listen for incoming client messages."""
    # Initial join message
    msg = client.get_message()
    if msg is None:
        client.send_message(Message(MessageType.FAIL, "", "").encode())
        return

    client.set_name(msg.author)
    forward_message(clients, client, msg)

    # Add the client to the list
    clients.add(client)

    # Print who has joined
    if show_actions:
        print(Fore.GREEN + f'\n"{client.name}" has joined!' + Style.RESET_ALL)

    # Infinite loop for receiving
    while True:
        # Get the message
        msg = client.get_message()
        if msg is None:
            break

        forward_message(clients, client, msg)

        # Do some internal work
        if msg.type == MessageType.NAME:
            client.set_name(msg.content)

        elif msg.type == MessageType.QUIT:
            break

    # Remove the client from the list
    clients.remove(client)

    # Print who has left
    if show_actions:
        print(Fore.RED + f'\n"{client.name}" has left.' + Style.RESET_ALL)


def forward_message(clients: set[Client], sender: Client | None, msg: Message):
    """Relay a message to all clients."""
    # Loop through all clients
    for client in clients:

        # Check if the client is not the sender
        if client != sender:
            client.send_message(msg.encode())


if __name__ == "__main__":
    main()
