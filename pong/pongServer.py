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

#Global game state variables
screen_width = 960
screen_height = 720
left_paddle_y = screen_height // 2
right_paddle_y = screen_height // 2
ball_x = screen_width // 2
ball_y = screen_height // 2
score_left = 0
score_right = 0
game_lock = threading.Lock()  # Lock to synchronize access to game state variables

def recv_exact(conn, num_bytes):
    """Receive exactly num_bytes from the socket."""
    data = b''
    while len(data) < num_bytes:
        chunk = conn.recv(num_bytes - len(data))
        if not chunk:
            raise ConnectionError("Connection closed before receiving all data")
        data += chunk
    return data

def handle_client(conn, addr, num):
    global screen_width, screen_height, left_paddle_y, right_paddle_y, ball_x, ball_y, score_left, score_right
    print(f"[NEW CONNECTION] {addr}")
    conn.send(num.to_bytes(1, 'big'))  # Send player number to client
    conn.send(screen_width.to_bytes(4, 'big'))  # Send screen width to client
    conn.send(screen_height.to_bytes(4, 'big'))  # Send screen height to client
    while True:
        try:
            paddle_y = int.from_bytes(recv_exact(conn, 4), 'big')  # Receive paddle Y position from client
            ball_x_recv = int.from_bytes(recv_exact(conn, 4), 'big')  # Receive ball X position from client
            ball_y_recv = int.from_bytes(recv_exact(conn, 4), 'big')  # Receive ball Y position from client
            l_score = int.from_bytes(recv_exact(conn, 4), 'big')  # Receive left player score from client
            r_score = int.from_bytes(recv_exact(conn, 4), 'big')  # Receive right player score from client

            #Update global state based on this player this thread is responsible for
            if num == 1:
                with game_lock:
                    left_paddle_y = paddle_y
            else:
                with game_lock:
                    right_paddle_y = paddle_y
            # Process the data and update game state here
            # You will need to send updates to both clients about the game state
            with game_lock:
                ball_x = ball_x_recv
                ball_y = ball_y_recv
                score_left = l_score
                score_right = r_score
            print(f"Player {num} - Paddle Y: {paddle_y}, Ball X: {ball_x}, Ball Y: {ball_y}, Score Left: {score_left}, Score Right: {score_right}")
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
