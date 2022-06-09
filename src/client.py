"""Client side of this application."""

from threading import Thread

from client_window import ClientWindow
from wrappers import MessageType, Server


def receive_messages(server: Server, window: ClientWindow):
    """Recieve messages."""
    while True:
        msg = server.get_message()
        if msg is None:
            continue

        if window.name is None:
            continue

        window.add_chat(msg)

        if msg.type == MessageType.FAIL:
            break


def main():
    """Set up clients and threads."""
    # Try to connect to the server
    server = Server()
    if server.connect() is False:
        print("Could not connect.")
        return

    window = ClientWindow(server)

    # Set up the receiving thread
    receive_thread = Thread(target=receive_messages, args=(server, window))
    receive_thread.daemon = True
    receive_thread.start()

    # Start the GUI
    window.start()


if __name__ == "__main__":
    main()
