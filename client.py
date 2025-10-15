import socket
import threading
import sys
from tkinter import Tk, Text, Entry, Button, END, Label, Frame
from tkinter import Toplevel, simpledialog
from datetime import datetime

#Define client GUI objects
class ChatClientGUI:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.is_connected = False

        #Tkinter window
        self.window = Tk()
        self.window.title(f"Client Chatbot - Connected to {host}:{port}")
        self.window.geometry("500x500")
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.configure(bg="#808080") 
        
        #Chat history - TO BE IMPLEMENTED
        self.chat_label = Label(self.window, text="YapSesh Chat History:", padx=5, pady=5, bg="#808080")
        self.chat_label.pack(fill='x')

        #Chat log where messages are displayed
        self.chat_log = Text(self.window, state='disabled', wrap='word', height=20, width=50, bg="#303030", fg="white")
        self.chat_log.pack(padx=10, pady=5, fill='both', expand=True)
        
        #Textbox font colors
        self.chat_log.tag_config('System', foreground='lightblue') 
        self.chat_log.tag_config('Error', foreground='red', font=('Helvetica', 10, 'bold'))
        self.chat_log.tag_config('Client', foreground='white', font=('Helvetica', 10, 'bold'))
        self.chat_log.tag_config('Server', foreground='lightgreen', font=('Helvetica', 10))

        #Input frame with buttons
        input_frame = Frame(self.window, bg="#f0f0f0")
        input_frame.pack(padx=10, pady=(0, 10), fill='x')

        #Input text field
        self.input_field = Entry(input_frame, bg="white", fg="#333", borderwidth=2, relief="groove")
        self.input_field.bind("<Return>", self.send_message_event)
        self.input_field.pack(side='left', fill='x', expand=True, ipady=3)
        self.input_field.focus_set()

        #Send button
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

        #End chat button
        self.end_chat_button = Button(input_frame, 
                                      text="End Chat", 
                                      command=self.on_closing, 
                                      bg='#dc3545', 
                                      fg='white',
                                      relief="raised",
                                      activebackground='#c82333',
                                      activeforeground='white',
                                      highlightbackground='#dc3545',
                                      padx=10)
        self.end_chat_button.pack(side='right', padx=(5, 5)) #Added padding on both sides to separate it

        #Connect immediately
        self.attempt_connection()

    #Networking functions

    #Try to connect to server
    def attempt_connection(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.is_connected = True
            self.update_chat_log(f"--- Connected to server at {self.host}:{self.port} ---\n", "System")
            
            #Start receive thread
            threading.Thread(target=self.receive_messages, daemon=True).start()

            #Let the other clients know this client has joined
            try:
                self.client_socket.sendall("joined".encode())
            except:
                pass
        #Close window on connection error
        except Exception as e:
            self.update_chat_log(f"Connection Error: Could not connect to server ({e})\n", "Error")
            self.is_connected = False
            self.window.after(3000, self.window.destroy)

    #Listen for messages forwarded from server
    def receive_messages(self):
        while self.is_connected:
            try:
                message = self.client_socket.recv(1024)
                if not message:
                    self.update_chat_log("\n--- Server Disconnected ---\n", "System")
                    self.is_connected = False
                    break
                
                self.update_chat_log(message.decode() + "\n", "Server")
            except Exception:
                if self.is_connected:
                    self.update_chat_log("\n--- An error occurred during reception. ---\n", "Error")
                self.is_connected = False
                break
        
        #Close thread and window on disconnect
        if self.client_socket:
            self.client_socket.close()
        
        if self.window.winfo_exists():
            self.window.after(100, self.window.destroy)

    #Event to send message triggered by Enter key press
    def send_message_event(self, event=None):
        self.send_message()

    #Send message to server/other clients
    def send_message(self):
        if not self.is_connected:
            self.update_chat_log("Cannot send: not connected to server.\n", "Error")
            return

        #Get the input from the input field typed by user
        message = self.input_field.get()
        self.input_field.delete(0, END)

        #Don't send message if it's empty
        if not message.strip():
            return

        #Display client's message to itself
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.update_chat_log(f"[{timestamp}] You: {message}\n", "Client")

        try:
            #Send message to server/other clients
            self.client_socket.sendall(message.encode())
        except Exception as e:
            self.update_chat_log(f"Send Error: {e}\n", "Error")
            self.is_connected = False
    
    #Update chatbox field when new messages are sent 
    def update_chat_log(self, message, sender):
        self.chat_log.config(state='normal')
        self.chat_log.insert(END, message, sender)
        self.chat_log.config(state='disabled')
        self.chat_log.see(END)

    #Close window and socket on disconnect
    def on_closing(self):
        if self.is_connected and self.client_socket:
            try:
                self.client_socket.sendall("exit".encode())
            except:
                pass
            self.is_connected = False
            self.client_socket.close()
        self.window.destroy()

#Prompt user for port to connect to server
def get_port_from_user():
    root = Tk()
    root.withdraw() #Hide main window
    
    port = -1
    while port < 1025 or port > 65535:
        port_str = simpledialog.askstring("Port Required", 
                                        "Welcome! Please specify the TCP port (1025-65535) you would like to connect to:",
                                        parent=root)
        if port_str is None: #Close window if user clicks cancel
            root.destroy()
            return None 
        try:
            port = int(port_str)
            if port < 1025 or port > 65535:
                #Show error if invalid port, prompt again
                simpledialog.messagebox.showerror("Error", "Invalid port. Please use a port between 1025 and 65535.")
        except ValueError:
            #Show error if non-number inputted
            simpledialog.messagebox.showerror("Error", "Invalid input. Please enter a number.")
            port = -1
    root.destroy()
    return port

#Main program

if __name__ == "__main__":
    HOST = '127.0.0.1' 
    port = get_port_from_user()
    
    if port:
        app = ChatClientGUI(HOST, port)
        app.window.mainloop()