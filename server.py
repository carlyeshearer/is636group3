# Authors: Carly Shearer (WH10650), Liza, Amy
# Course: IS/HCC636
# Project: Client/Server Chatbot
# Descrption: This program implements a simple server with a GUI, which asks the user for a
# TCP port to listen on and sends and receives messages from multiple clients.

import socket
import threading
import sys
from datetime import datetime
from tkinter import Tk, Text, Entry, Button, END, Label, Frame, simpledialog, messagebox
from tkinter.scrolledtext import ScrolledText

# Global variables (moved into a class structure where possible, but necessary for threading)
HOST = '127.0.0.1'
clients = []
clients_lock = threading.Lock()
server_socket = None #Will be initialized in start_server_gui
history_file = "history.txt"
timestamp = datetime.now().strftime("%H:%M:%S")

# Define GUI Class for Server
class ChatServerGUI:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.is_running = True

        # Tkinter window
        self.window = Tk()
        self.window.title(f"Server Chatbot - Listening on {host}:{port}")
        self.window.geometry("600x500")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.configure(bg="#808080")

        # Chat history label
        Label(self.window, text="YapSesh Server Log:", padx=5, pady=5, bg="#808080", fg="white").pack(fill='x')

        # Chat log where messages are displayed
        self.chat_log = ScrolledText(self.window, state='disabled', wrap='word', height=20, width=50, bg="#303030", fg="white")
        self.chat_log.pack(padx=10, pady=5, fill='both', expand=True)

        # Textbox font colors & styles
        self.chat_log.tag_config('System', foreground='lightblue', font=('Courier', 12)) 
        self.chat_log.tag_config('Error', foreground='red', font=('Courier', 12, 'bold'))
        self.chat_log.tag_config('Client', foreground='lightgreen', font=('Courier', 12)) # Changed to 'lightgreen'
        self.chat_log.tag_config('Server', foreground='white', font=('Courier', 12, 'bold')) # Changed to 'white'

        # Input frame with buttons
        input_frame = Frame(self.window, bg="#808080")
        input_frame.pack(padx=0, pady=(0, 10), fill='x')

        # Input text field
        self.input_field = Entry(input_frame, bg="white", fg="#333", borderwidth=2, relief="groove")
        self.input_field.bind("<Return>", self.send_message_event)
        self.input_field.pack(side='left', fill='x', expand=True, ipady=3)
        self.input_field.focus_set()

        # Send button
        self.send_button = Button(input_frame,
                                 text="Send",
                                 command=self.send_message,
                                 bg='blue',
                                 fg='white',
                                 relief="raised",
                                 activebackground='blue',
                                 activeforeground='white',
                                 highlightbackground='blue',
                                 padx=10)
        self.send_button.pack(side='right', padx=(5, 0))
        
        # End chat button
        self.end_chat_button = Button(input_frame, 
                                      text="End Server", 
                                      command=self.on_closing, 
                                      bg='#dc3545', 
                                      fg='white',
                                      relief="raised",
                                      activebackground='#c82333',
                                      activeforeground='white',
                                      highlightbackground='#dc3545',
                                      padx=10)
        self.end_chat_button.pack(side='right', padx=(5, 5)) 

        # Start the server logic in a separate thread
        threading.Thread(target=self.start_server_logic, daemon=True).start()

    # --- GUI Update Function ---
    def update_chat_log(self, message, sender='System'):
        """Safely update the GUI chat log from any thread."""
        self.chat_log.config(state='normal')
        self.chat_log.insert(END, message, sender)
        self.chat_log.config(state='disabled')
        self.chat_log.see(END)

    #Log messages to history of chats file
    def log_message(self, message):
        with open("history.txt", "a", encoding="utf-8") as file:
            file.write(f"{message}")

    # Send messages sent by one client to all other clients
    def forward_messages(self, message, sender_socket=None):
        global clients, clients_lock
        with clients_lock:
            # Send the message to everyone
            for client in clients:
                if client != sender_socket:
                    try:
                        client.sendall(message)
                    except:
                        # Clean up disconnected client
                        client.close()
                        clients.remove(client)

    # Send welcome message to newly connected clients
    def send_welcome_message(self, client_connected):
        global clients, clients_lock
        welcome_message = "Welcome! Chat with the server by typing your message below. To exit, please click the \"End Chat\" button.\n"
        with clients_lock:
            try:
                client_connected.send(welcome_message.encode())
            except Exception as e:
                self.update_chat_log(f"ERROR sending welcome: {e}\n", "Error")
                client_connected.close()
                clients.remove(client_connected)

    # Handle messages from connected clients
    def handle_clients(self, client_socket, client_address):
        global clients, clients_lock
        # client_address is a tuple: (IP_ADDRESS, PORT). We only want the port [1].
        client_port = client_address[1]
        self.update_chat_log(f"New connection from ({client_port})\n", "System") 

        with clients_lock:
            clients.append(client_socket)

        self.send_welcome_message(client_socket)
        self.log_message(f"[{timestamp}] Chat initiated\n")
        self.log_message(f"[{timestamp}] Server: Welcome! Chat with the server by typing your message below. To exit, please click the \"End Chat\" button.\n")

        try:
            while self.is_running:
                message = client_socket.recv(1024)
                if not message:
                    break

                # Display received messages to server and forward to others
                decoded_msg = message.decode()
                # Use only the port in the message displayed to server and forwarded to clients
                formatted_server_log = f"[{timestamp}] Client {client_port}: {decoded_msg}\n"
                formatted_client_msg = f"[{timestamp}] Client {client_port}: {decoded_msg}"

                self.update_chat_log(formatted_server_log, "Client")
                self.log_message(f"[{timestamp}] Client {client_port}: {decoded_msg}\n")
                self.forward_messages(formatted_client_msg.encode(), sender_socket=client_socket)

        except Exception as e:
            if self.is_running: # Only log error if not a graceful shutdown
                #self.update_chat_log(f"Client handler error for {client_address}: {e}\n", "Error")
                print(f"Client handler error for {client_address}: {e}\n", "Error")

        # Remove client if they disconnect
        finally:
            with clients_lock:
                if client_socket in clients:
                    clients.remove(client_socket)
            client_socket.close()
            self.update_chat_log(f"Client disconnected: ({client_port})\n", "System")

    # The main server loop 
    def start_server_logic(self):
        global clients_lock
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            self.update_chat_log(f"Server listening on {self.host}:{self.port}\n", "System")

            while self.is_running:
                try:
                    # Set a timeout for accept so the loop can check self.is_running
                    self.server_socket.settimeout(0.5)
                    client_socket, client_address = self.server_socket.accept()
                    threading.Thread(target=self.handle_clients, args=(client_socket, client_address), daemon=True).start()
                except socket.timeout:
                    continue
                except socket.error as e:
                    if self.is_running: # Log socket error only if server is meant to be running
                        self.update_chat_log(f"Server accept error: {e}\n", "Error")
                    break
        except Exception as e:
            self.update_chat_log(f"Failed to start server: {e}\n", "Error")
            self.is_running = False
            self.window.after(3000, self.window.destroy) # Close GUI on critical error
        finally:
            self.cleanup_server()


    # Event to send message triggered by Enter key press
    def send_message_event(self, event=None):
        self.send_message()

    # Send message from server to clients
    def send_message(self):
        message = self.input_field.get()
        self.input_field.delete(0, END)

        if not message.strip():
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_server_log = f"[{timestamp}] Server: {message}\n"
        formatted_client_msg = f"[{timestamp}] Server: {message}"

        self.update_chat_log(formatted_server_log, "Server")
        self.log_message(f"[{timestamp}] Server: {message}\n")
        self.forward_messages(formatted_client_msg.encode())

  # Cleanup socket to shutdown server
    def cleanup_server(self):
        global clients, clients_lock
        if self.server_socket:
            self.server_socket.close()
        
        # Close all connected clients
        with clients_lock:
            for c in clients:
                try:
                    c.sendall("Server shutting down.".encode())
                    c.close()
                except:
                    pass
            clients.clear()


    # Close window and socket on disconnect
    def on_closing(self):
        self.is_running = False
        self.update_chat_log("\nShutting down server...\n", "System")
        
        # Give the main server thread a moment to exit the accept loop
        # Then safely destroy the window
        threading.Thread(target=lambda: self.window.after(100, self.window.destroy)).start()

# Prompt user for TCP port to listen on
def get_port_from_user():
    root = Tk()
    root.withdraw() # Hide main window

    port = -1
    while port < 1025 or port > 65535:
        port_str = simpledialog.askstring("Port Required",
                                        "Welcome! Please specify the TCP port (1025-65535) you would like to listen on:",
                                        parent=root)
        if port_str is None: # Close window if user clicks cancel
            root.destroy()
            return None
        try:
            port = int(port_str)
            if port < 1025 or port > 65535:
                # Show error if invalid port, prompt again
                messagebox.showerror("Error", "Invalid port. Please use a port between 1025 and 65535.")
        except ValueError:
            # Show error if non-number inputted
            messagebox.showerror("Error", "Invalid input. Please enter a number.")
            port = -1
    root.destroy()
    return port

if __name__ == "__main__":
    port = get_port_from_user()

    if port:
        app = ChatServerGUI(HOST, port)
        app.window.mainloop()