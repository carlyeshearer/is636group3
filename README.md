This project is a simple Python chatbot where a client and server are able to send messages to each other.

Server.py implements the logic for the server.
- Uses sockets and threads to send/receive messages from clients
- Forwards messages from one client to other clients

Client.py implements the logic for the client.
- Uses sockets to establish connection to server
- Each client runs in its own thread to send/receive messages to/from server

This program requires Python 3 to be installed. To run the program, the server must be started first. To start the server, run the following in a terminal:
- python3 server.py

To connect a client, run the following in a terminal. To connect multiple clients, this command should be run separately with one terminal per client:
- python3 client.py

Ensure that the specified port is the same for both the server and the clients, and that the server begins listening before the clients connect.

Bonus Features Implemented:
- Multiple client support
- GUI
- Timestamps
- Unique IDs for each client
- Chat history log

References: 
- https://www.youtube.com/watch?v=8Q7OF8TP6u0
- https://medium.com/@denizhalil/advanced-socket-programming-with-python-multi-client-and-server-communication-c0416836c3bd
- https://www.robotexchange.io/t/-how-to-create-tcp-ip-server-that-can-handle-multi-client-with-python-the-client-could-be-laptop-and-robot/3317

