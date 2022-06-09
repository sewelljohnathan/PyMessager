"""Docstring."""

import tkinter
import tkinter.messagebox

from wrappers import Message, MessageType, Server

BACKGROUND_COLOR = "gray"


class ClientWindow:
    """Represents a window for the client to interact with."""

    def __init__(self, server: Server):
        """Initialize the client window."""
        self.server = server
        self.name = None

        self.create_window()
        self.create_header_frame()
        self.create_name_frame()
        self.create_chat_frame()
        self.create_msg_input_frame()

    def create_window(self):
        """Create and initialize the close frame."""
        self.window = tkinter.Tk()
        self.window.title("PyMessager")
        self.window.geometry("400x600")
        self.window.configure(background=BACKGROUND_COLOR)
        self.window.iconphoto(False, tkinter.PhotoImage(file="icon.png"))

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_header_frame(self):
        """Create and initialize the header."""
        self.header_frame = tkinter.Frame(
            self.window, pady=10, background=BACKGROUND_COLOR
        )

        self.title_label = tkinter.Label(
            self.header_frame,
            text="PyMessager",
            font=("Elephant", 25),
            background=BACKGROUND_COLOR,
        )
        self.title_label.pack()
        self.subtitle_label = tkinter.Label(
            self.header_frame,
            text="A Python Chat Application!",
            font=("Elephant", 11),
            background=BACKGROUND_COLOR,
        )
        self.subtitle_label.pack()

        self.header_frame.pack()

    def create_name_frame(self):
        """Create and initialize the name frame."""
        self.name_frame = tkinter.Frame(self.window, background=BACKGROUND_COLOR)

        self.name_label = tkinter.Label(
            self.name_frame,
            text="Your Name:",
            font=("Arial Bold", 12),
            background=BACKGROUND_COLOR,
        )
        self.name_label.pack()

        self.name_input = tkinter.StringVar()
        self.name_entry = tkinter.Entry(
            self.name_frame,
            textvariable=self.name_input,
            font=("Arial", 12),
        )
        self.name_entry.bind("<Return>", self.send_name)
        self.name_entry.focus_set()
        self.name_entry.pack()

        self.name_button = tkinter.Button(
            self.name_frame,
            text="Change Name",
            font=("Arial Bold", 10),
        )
        self.name_button.bind("<Button-1>", self.send_name)
        self.name_button.bind("<Return>", self.send_name)
        self.name_button.pack(pady=10)

        self.name_frame.pack()

    def create_chat_frame(self):
        """Create and initialize the chat frame."""
        self.chat_frame = tkinter.Frame(
            self.window, padx=20, pady=10, background=BACKGROUND_COLOR
        )

        self.chat_scrollbar = tkinter.Scrollbar(self.chat_frame)
        self.chat_scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        self.chat_box = tkinter.Text(
            self.chat_frame, height=15, width=50, yscrollcommand=self.chat_scrollbar.set
        )
        self.chat_box.config(state=tkinter.DISABLED)
        self.chat_box.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.chat_box.pack()
        self.chat_scrollbar.config(command=self.chat_box.yview)

        self.chat_frame.pack()

    def create_msg_input_frame(self):
        """Create and initialize the msg input frame."""
        self.msg_input_frame = tkinter.Frame(
            self.window, pady=10, background=BACKGROUND_COLOR
        )

        self.msg_input_label = tkinter.Label(
            self.msg_input_frame,
            text="Send a Message",
            font=("Arial Bold", 12),
            background=BACKGROUND_COLOR,
        )
        self.msg_input_label.pack()

        self.msg_input_entry = tkinter.Text(
            self.msg_input_frame,
            wrap=tkinter.WORD,
            font=("Arial", 12),
            width=20,
            height=3,
        )
        self.msg_input_entry.bind("<Return>", self.send_chat)
        self.msg_input_entry.pack()

        self.name_button = tkinter.Button(
            self.msg_input_frame, text="Send", font=("Arial Bold", 10), width=15
        )
        self.name_button.bind("<Button-1>", self.send_chat)
        self.name_button.pack(pady=10)

        self.msg_input_frame.pack()

    def start(self):
        """Start the window main loop."""
        self.window.mainloop()

    def send_chat(self, event=None):
        """Send a chat message to the server."""
        # Dont send unless a name is set
        if self.name is None:
            tkinter.messagebox.showwarning(
                "Wait!", "Please set your name before sending a message."
            )
            self.name_entry.focus_set()
            return

        # Send the message to the server
        text_input = self.msg_input_entry.get("1.0", "end-1c").rstrip()
        msg = Message(MessageType.CHAT, self.name, text_input)

        if msg and text_input != "":
            self.server.send_message(msg.encode())
            self.add_chat(msg)

        # Recreate the text box to get around the newline addition
        self.msg_input_frame.destroy()
        self.create_msg_input_frame()
        self.msg_input_entry.focus_set()

    def send_name(self, event=None):
        """Send a name change to the server."""
        # Get the input
        new_name = self.name_input.get()
        if len(new_name) > 10:
            tkinter.messagebox.showwarning("Wait!", "Please choose a shorter name.")
            return

        # Create the message
        if self.name is None:
            msg = Message(MessageType.JOIN, new_name, "")
        else:
            msg = Message(MessageType.NAME, self.name, new_name)

        # Change internals
        self.name_label.config(text=f"Your Name: {new_name}")
        self.name = new_name

        # Send the message
        self.server.send_message(msg.encode())
        self.add_chat(msg)

    def on_closing(self):
        """Handle disconnecting the client."""
        if self.name:
            msg = Message(MessageType.QUIT, self.name, "")
            self.server.send_message(msg.encode())

        self.window.quit()

    def add_chat(self, msg: Message):
        """Append a message to the chatbox."""
        # Create the content
        content = ""
        if msg.type == MessageType.JOIN:

            if msg.author == self.name:
                content = "You joined!"
            else:
                content = f'"{msg.author}" joined!'

        elif msg.type == MessageType.CHAT:

            if msg.author == self.name:
                content = "Me: "
            else:
                content = f"{msg.author}: "

            content += msg.content

        elif msg.type == MessageType.NAME:
            content = f'"{msg.author}" changed their name to "{msg.content}"'

        elif msg.type == MessageType.CAST:
            content = f"SERVER: {msg.content}"

        elif msg.type == MessageType.QUIT:
            content = f'"{msg.author}" left.'

        elif msg.type == MessageType.FAIL:
            content = "You were disconnected."

        # Add the message to the chat box
        self.chat_box.config(state=tkinter.NORMAL)
        self.chat_box.insert(tkinter.END, f"{content}\n")
        self.chat_box.config(state=tkinter.DISABLED)

        # Auto scroll to the end if the client is not looking at past messages
        if self.chat_scrollbar.get()[1] > 0.9:
            self.chat_box.see(tkinter.END)
