#Authors: Carly Shearer (WH10650), Liza, Amy
#Course: IS/HCC636
#Project: Client/Server Chatbot
#Descrption: This program implements a simple server, which asks the user for a 
#TCP port to listen on and sends and receives messages from a client.

import socket
import threading
import sys
from datetime import datetime

#Global variables
timestamp = datetime.now()
format_timestamp = timestamp.strftime("%H:%M:%S")

#Define functions

#Print server/client messages
def print_message(sender, message, prompt):
    #Erase the current input line, print message, then reprint the prompt
    print(f"\r\n{sender} ({format_timestamp}): {message}\n{prompt}", end="", flush=True)

#Send messages sent by one client to all other clients
def forward_messages(message, sender_socket=None):
    #Lock thread to ensure no race condition between client threads
    with clients_lock:
        #Send the client's message to everyone other than the client that sent the message
        for client in clients:
            if client != sender_socket:
                try:
                    client.sendall(message)
                except:
                    client.close()
                    clients.remove(client)

#Handle messages from connected clients
def handle_clients(client_socket, client_address):
    print(f"New connection from {client_address}")
    #Lock socket before appending to ensure no race conditions
    with clients_lock:
        clients.append(client_socket)

    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            
            #Display received messages to server and clients
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted = f"[{timestamp}] Client {client_address}: {message.decode()}"
            print(formatted)
            forward_messages(formatted.encode(), sender_socket=client_socket)
    except Exception:
        print(f"Disconnecting clients...")
    #Remove client if they disconnect
    finally:
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        client_socket.close()
        print(f"Client disconnected: {client_address}")

#Send message from server to clients
def send_message():
    while True:
        message = input("")
        if message.lower() == "exit":
            print("Shutting down server.")
            server_socket.close()
            with clients_lock:
                for c in clients:
                    c.close()
            sys.exit(0)
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] Server: {message}"
        print(formatted)
        forward_messages(formatted.encode())

#Initialize server and threads
def start_server(port):
    #Create thread for server to send messages
    threading.Thread(target=send_message, daemon=True).start()
    welcome_message = "Welcome! Chat with the server by typing your message below. To exit, please enter \"exit\".\n"

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            forward_messages(welcome_message.encode())
            threading.Thread(target=handle_clients, args=(client_socket, client_address), daemon=True).start()
    except Exception:
        print("\nServer shutting down...")
    #If server shuts down, close all connected clients
    finally:
        server_socket.close()
        with clients_lock:
            for c in clients:
                c.close()

#Main program

#Prompt user for TCP port to listen on
port = int(input("Welcome! Please specify the TCP port you would like to listen on: "))

#Validate user input
while((port < 1025) | (port > 65535)):
    print("Error: Invalid. Please try again.")
    port = int(input("Welcome! Please specify the TCP port you would like to listen on: "))

host = '127.0.0.1'
clients = []
clients_lock = threading.Lock()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen()
print(f"Server listening on {host}:{port}")

start_server(port)