#Authors: Carly Shearer (WH10650), Liza, Amy
#Course: IS/HCC636
#Project: Client/Server Chatbot
#Descrption: This program implements a simple client, which asks the user for a 
#TCP port to connect to and sends and receives messages from a server.

import socket
import threading
from datetime import datetime

#Global variables
timestamp = datetime.now()
format_timestamp = timestamp.strftime("%H:%M:%S")

#Define functions

def print_message(sender, message, prompt):
    #Erase the current input line, print message, then reprint the prompt
    print(f"\r\n{sender} ({format_timestamp}): {message}\n{prompt}", end="", flush=True)

def receive_messages(socket):
    while True:
        try:
            message = socket.recv(1024)
            if not message:
                print("\nError: client disconnected from server.")
                break
            print(f"{message.decode()}")
        except Exception:
            break

def start_client(port):
    host = '127.0.0.1'
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")

        # Start thread to listen for incoming messages
        threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

        while True:
            message = input("")
            if message.strip().lower() == "exit":
                break
            client_socket.sendall(message.encode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Client disconnected.")

#Main program

#Prompt user for TCP port to listen on
port = int(input("Welcome! Please specify the TCP port you would like to connect to: "))

#Validate user input
while port < 1025 or port > 65535:
    print("Error: Invalid. Please try again.")
    port = int(input("Welcome! Please specify the TCP port you would like to connect to: "))

start_client(port)