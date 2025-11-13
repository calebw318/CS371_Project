# =================================================================================================
# Contributing Authors:	    <Anyone who touched the code>
# Email Addresses:          <Your uky.edu email addresses>
# Date:                     <The date the file was last edited>
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games

HOST = "0.0.0.0"
PORT = 65432

def handle_client(conn, addr, num):
    print(f"[NEW CONNECTION] {addr}")
    screen_width = 960
    screen_height = 720
    conn.send(num.to_bytes(1, 'big'))  # Send player number to client
    conn.send(screen_width.to_bytes(4, 'big'))  # Send screen width to client
    conn.send(screen_height.to_bytes(4, 'big'))  # Send screen height to client
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            # Process the data and update game state here
            # You will need to send updates to both clients about the game state
        except:
            break
    conn.close()
    print(f"[DISCONNECTED] {addr}")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

num = 0

while True:
    conn, addr = server_socket.accept()
    num += 1
    threading.Thread(target=handle_client, args=(conn, addr, num)).start()
    num -= 1  # Decrement num to keep track of player numbers correctly
