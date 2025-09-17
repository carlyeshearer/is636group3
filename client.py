#Authors: Carly Shearer (WH10650), Liza, Amy
#Course: IS/HCC636
#Project: Client/Server Chatbot
#Descrption: This program implements a simple client, which asks the user for a 
#TCP port to connect to and sends and receives messages from a server.

import socket
from threading import Thread
import os

#reference videos: https://www.youtube.com/watch?v=8Q7OF8TP6u0

#Define functions

def print_message(sender, message, prompt):
    #Erase the current input line, print message, then reprint the prompt
    print(f"\r\n{sender}: {message}\n{prompt}", end="", flush=True)

#Send a message to the server
def send_message(client_socket):
    #Send whatever is the input by the client as message
    try:
        while True:
            message = input("Client: ")
            if message.strip().lower() == "exit":
                client_socket.send(message.encode())
                break
            client_socket.send(message.encode())
    #If there is an error, close the connection
    except (ConnectionAbortedError, OSError):
        print("Connection closed.")

#Receive a message from the server
def receive_message(client_socket):
    try:
        while True:
            server_message = client_socket.recv(1024).decode()
            if not server_message:
                print("Server disconnected.")
                break
            if server_message.strip().lower() == "exit":
                print("Server ended the chat.")
                break
            print_message("Server", server_message, "Client: ")
    #If there is an error, close the connection
    except (ConnectionAbortedError, OSError):
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
port = int(input("Welcome! Please specify the TCP port you would like to connect to: "))

#Validate user input
while port < 1025 or port > 65535:
    print("Error: Invalid. Please try again.")
    port = int(input("Welcome! Please specify the TCP port you would like to connect to: "))

#Create client socket listen on localhost
host = '127.0.0.1'
client_socket = socket.socket()
client_socket.connect((host, port))

#Display messaging output
start_messaging(client_socket)