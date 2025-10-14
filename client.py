import socket
import threading
from tkinter import Tk, Text, Entry, Button, END, Scrollbar, Label
from tkinter import Toplevel, simpledialog
from datetime import datetime

class ChatClientGUI:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.is_connected = False

        # --- 1. Tkinter Setup ---
        self.window = Tk()
        self.window.title("Client Chatbot")
        self.window.geometry("500x500")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Chat History Display
        self.chat_label = Label(self.window, text="Chat History:", padx=5, pady=5)
        self.chat_label.pack(fill='x')

        self.chat_log = Text(self.window, state='disabled', wrap='word', height=20, width=50)
        self.chat_log.pack(padx=10, pady=5, fill='both', expand=True)

        # Input Field
        self.msg_label = Label(self.window, text="Your Message:", padx=5, pady=5)
        self.msg_label.pack(fill='x')
        
        self.input_field = Entry(self.window)
        self.input_field.bind("<Return>", self.send_message_event)
        self.input_field.pack(padx=10, pady=5, fill='x')

        # Send Button
        self.send_button = Button(self.window, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=5)

        # Initial connection (moved from main program logic)
        self.attempt_connection()

    # --- 2. Networking Functions ---

    def attempt_connection(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.is_connected = True
            self.update_chat_log(f"--- Connected to server at {self.host}:{self.port} ---\n", "System")
            
            # Start the non-blocking receive thread immediately
            threading.Thread(target=self.receive_messages, daemon=True).start()

        except Exception as e:
            self.update_chat_log(f"Connection Error: {e}\n", "Error")
            self.is_connected = False
            self.window.after(3000, self.window.destroy) # Close window after 3s on error

    def receive_messages(self):
        """Runs in a separate thread to listen for server messages."""
        while self.is_connected:
            try:
                # Blocking call: waits for a message
                message = self.client_socket.recv(1024)
                if not message:
                    self.update_chat_log("\n--- Server Disconnected ---\n", "System")
                    self.is_connected = False
                    break
                
                # Decode and display the message
                self.update_chat_log(message.decode() + "\n", "Server")

            except Exception:
                if self.is_connected:
                    self.update_chat_log("\n--- An error occurred during reception. ---\n", "Error")
                self.is_connected = False
                break
        
        if self.client_socket:
            self.client_socket.close()

    def send_message_event(self, event=None):
        """Handles the Enter key press."""
        self.send_message()

    def send_message(self):
        """Sends the message typed by the user."""
        if not self.is_connected:
            self.update_chat_log("Cannot send: not connected to server.\n", "Error")
            return

        message = self.input_field.get()
        self.input_field.delete(0, END) # Clear the input field

        if not message.strip():
            return

        # Display client's message locally
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.update_chat_log(f"[{timestamp}] You: {message}\n", "Client")

        try:
            # Send the message over the socket
            self.client_socket.sendall(message.encode())
        except Exception as e:
            self.update_chat_log(f"Send Error: {e}\n", "Error")
            self.is_connected = False

    # --- 3. GUI Update Functions ---
    
    def update_chat_log(self, message, sender):
        """Safely updates the Tkinter Text widget."""
        self.chat_log.config(state='normal')
        
        # Apply color/font based on sender (optional, but good practice)
        tag = 'normal'
        if sender == "System":
            tag = 'system'
        elif sender == "Error":
            tag = 'error'
        elif sender == "Client":
            tag = 'client'
        elif sender == "Server":
            tag = 'server'

        self.chat_log.insert(END, message, tag)
        self.chat_log.config(state='disabled')
        self.chat_log.see(END) # Scroll to the bottom

    def on_closing(self):
        """Handles closing the window."""
        if self.is_connected and self.client_socket:
            # Optional: send a disconnect message or "exit" command
            try:
                self.client_socket.sendall("exit".encode())
            except:
                pass 
            self.is_connected = False
            self.client_socket.close()
        self.window.destroy()

def get_port_from_user():
    """Prompts the user for a valid port before launching the GUI."""
    root = Tk()
    root.withdraw() # Hide the main window
    
    port = -1
    while port < 1025 or port > 65535:
        port_str = simpledialog.askstring("Port Required", 
                                        "Welcome! Please specify the TCP port (1025-65535) you would like to connect to:",
                                        parent=root)
        if port_str is None: # User clicked cancel
            root.destroy()
            return None 
        try:
            port = int(port_str)
            if port < 1025 or port > 65535:
                # Optionally add a message box for invalid port
                simpledialog.messagebox.showerror("Error", "Invalid port. Please use a port between 1025 and 65535.")
        except ValueError:
             simpledialog.messagebox.showerror("Error", "Invalid input. Please enter a number.")
             port = -1

    root.destroy()
    return port

if __name__ == "__main__":
    HOST = '127.0.0.1' 
    port = get_port_from_user() # Use a dialog box for input
    
    if port:
        app = ChatClientGUI(HOST, port)
        app.window.mainloop()