import socket
import threading
import sys
from tkinter import Tk, Text, Entry, Button, END, Label
from tkinter import Toplevel, simpledialog # simpledialog is kept in case you want to use it later, but not used in the final version
from datetime import datetime

class ChatClientGUI:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.is_connected = False

        # --- 1. Tkinter Setup ---
        self.window = Tk()
        self.window.title(f"Client Chatbot - Connected to {host}:{port}")
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
        # Binds the Enter key to send the message
        self.input_field.bind("<Return>", self.send_message_event) 
        self.input_field.pack(padx=10, pady=5, fill='x')

        # Send Button
        self.send_button = Button(self.window, text="Send", command=self.send_message)
        self.send_button.pack(padx=10, pady=5)

        # Connect immediately
        self.attempt_connection()

    # --- 2. Networking Functions ---

    def attempt_connection(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.is_connected = True
            self.update_chat_log(f"--- Connected to server at {self.host}:{self.port} ---\n", "System")
            
            # Start the non-blocking receive thread
            threading.Thread(target=self.receive_messages, daemon=True).start()

        except Exception as e:
            self.update_chat_log(f"Connection Error: {e}\n", "Error")
            self.is_connected = False
            # Close the window after 3 seconds on failure
            self.window.after(3000, self.window.destroy) 

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
        
        # Ensure the GUI can be closed if the network thread breaks
        if self.window.winfo_exists():
            self.window.after(100, self.window.destroy)

    def send_message_event(self, event=None):
        """Triggered by the Enter key press."""
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
        
        # Basic tagging for color/font can go here if desired
        tag = 'normal' 
        
        self.chat_log.insert(END, message, tag)
        self.chat_log.config(state='disabled')
        self.chat_log.see(END) # Scroll to the bottom

    def on_closing(self):
        """Handles closing the window."""
        if self.is_connected and self.client_socket:
            # Send an 'exit' signal to the server before closing
            try:
                self.client_socket.sendall("exit".encode())
            except:
                pass 
            self.is_connected = False
            self.client_socket.close()
        self.window.destroy()

# ----------------- Main Execution Block (Uses sys.argv) -----------------

if __name__ == "__main__":
    HOST = '127.0.0.1' 
    
    # 1. Check for command-line argument (the port number)
    if len(sys.argv) != 2:
        print("Usage: python3 client.py <PORT>")
        sys.exit(1)

    try:
        # 2. Convert the argument to an integer (this is sys.argv[1])
        port = int(sys.argv[1])
        
        # 3. Validate the port range
        if port < 1025 or port > 65535:
            print("Error: Port must be between 1025 and 65535.")
            sys.exit(1)

    except ValueError:
        print("Error: Port must be a valid integer.")
        sys.exit(1)

    # 4. Launch the GUI
    app = ChatClientGUI(HOST, port)
    app.window.mainloop()