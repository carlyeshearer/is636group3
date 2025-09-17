#Authors: Carly Shearer (WH10650), Liza, Amy
#Course: IS/HCC636
#Project: Client/Server Chatbot
#Descrption: This program implements a simple server, which asks the user for a 
#TCP port to listen on and sends and receives messages from a client.

import socket
from threading import Thread
import os

#reference videos: https://www.youtube.com/watch?v=8Q7OF8TP6u0

#Define functions

#Print server/client messages
def print_message(sender, message, prompt):
    #Erase the current input line, print message, then reprint the prompt
    print(f"\r\n{sender}: {message}\n{prompt}", end="", flush=True)

#Send a message to the client
def send_message(client_socket):
    #Send initial welcome message
    welcome_message = "Welcome! Chat with the server by typing your message below. To exit, please enter \"exit\".\n"
    client_socket.send(welcome_message.encode())
   
    #Send whatever is the input by the server as message
    try:
        while True:
            message = input("Server: ")
            if message.strip().lower() == "exit":
                client_socket.send(message.encode())
                break
            client_socket.send(message.encode())
    #If there is an error, close the connection
    except (ConnectionResetError, ConnectionAbortedError, OSError):
        print("Connection closed.")

#Receive a message from the client
def receive_message(client_socket):
    try:
        while True:
            client_message = client_socket.recv(1024).decode()
            if not client_message:
                print("Client disconnected.")
                break
            if client_message.strip().lower() == "exit":
                print("Client ended the chat.")
                break
            print_message("Client", client_message, "Server: ")
    except (ConnectionResetError, ConnectionAbortedError, OSError):
        print("Connection closed.")
    finally:
        client_socket.close()

#Start threads and send initial message
def start_messaging(client_socket):
    receive_thread = Thread(target=receive_message, args=(client_socket,))
    receive_thread.start()
    send_message(client_socket)
    receive_thread.join()
    print("Chat session ended.")

#Main program

#Prompt user for TCP port to listen on
port = int(input("Welcome! Please specify the TCP port you would like to listen on: "))

#Validate user input
while((port < 1025) | (port > 65535)):
    print("Error: Invalid. Please try again.")
    port = int(input("Welcome! Please specify the TCP port you would like to listen on: "))

#Create server socket with socket type TCP and listen on localhost
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '127.0.0.1'
server_socket.bind((host, port))

#Specify number of connections
server_socket.listen(1)

#Display messaging output
print(f"Server listening on: {host}:{port}")
client_socket, address = server_socket.accept()
print(f"Connected to client at {address}")
start_messaging(client_socket)