# =================================================================================================
# Contributing Authors:	    Caleb West, Colton Courrejolles, Edwin Saldivar
# Email Addresses:          cgwe225@uky.edu, ckco240@uky.edu, esa301@uky.edu
# Date:                     November 24th, 2025
# Purpose:                  Implements server logic for the pong game, including threading
#                           to handle multiple clients at once.
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
PORT = 12345

#Global game state variables
screen_width: int = 960
screen_height: int = 720
left_paddle_y: int = screen_height // 2
right_paddle_y: int = screen_height // 2
ball_x: int = screen_width // 2
ball_y: int = screen_height // 2
score_left: int = 0
score_right: int = 0
game_lock: threading.Lock = threading.Lock()  # Lock to synchronize access to game state variables
last_sync: list[int] = [0,0]  # List to keep track of sync status for each player

#Author: Caleb West
#Purpose: receive *exactly* num_bytes bytes from the server, no more and no less
#Pre: the program needs to be receiving data in order for this to be called.
#Post: returns the data received and is able to receive the next variable to update.
def recv_exact(conn: socket.socket, num_bytes: int) -> bytes:
    """Receive exactly num_bytes from the socket."""
    data = b''
    while len(data) < num_bytes:
        chunk = conn.recv(num_bytes - len(data))
        if not chunk:
            raise ConnectionError("Connection closed before receiving all data")
        data += chunk
    return data

def handle_client(conn: socket.socket, addr: tuple[str, int], num: int) -> None:
    global screen_width, screen_height, left_paddle_y, right_paddle_y, ball_x, ball_y, score_left, score_right, last_sync
    print(f"[NEW CONNECTION] {addr}")
    #set TCP_NODELAY to reduce latency and prevent packets from getting bunched together
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
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
            #print(f"Player {num} - Paddle Y: {paddle_y}, Ball X: {ball_x}, Ball Y: {ball_y}, Score Left: {score_left}, Score Right: {score_right}")
            sync: int = int.from_bytes(recv_exact(conn, 4), 'big')  # Receive sync status from client
            if sync > last_sync[num-1]:
                last_sync[num-1] = sync
            if num == 1:
                conn.send(last_sync[1].to_bytes(4, 'big')) # Send opponent sync status to client
                conn.send(right_paddle_y.to_bytes(4, 'big'))  # Send opponent paddle Y position to client
            elif num == 2:
                conn.send(last_sync[0].to_bytes(4, 'big')) # Send opponent sync status to client
                conn.send(left_paddle_y.to_bytes(4, 'big'))  # Send opponent paddle Y position to client

            #flag: bool = bool(int.from_bytes(recv_exact(conn, 1), 'big'))  # Receive flag from client
            #if flag:
            conn.send(ball_x.to_bytes(4, 'big'))  # Send ball X position to client
            conn.send(ball_y.to_bytes(4, 'big'))  # Send ball Y position to client
            conn.send(score_left.to_bytes(4, 'big'))  # Send left player score to client
            conn.send(score_right.to_bytes(4, 'big'))  # Send right player score to client
        except:
            break
    conn.close()
    print(f"[DISCONNECTED] {addr}")

server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

num = 0

while True:
    conn, addr = server_socket.accept()
    num += 1
    threading.Thread(target=handle_client, args=(conn, addr, num), daemon=True).start()
