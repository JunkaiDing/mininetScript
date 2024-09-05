import ctypes
import socket
import struct
import os

# Load the shared C library
tile_lib = ctypes.CDLL('./libtile_viewport.so')

# Define the argument types for the schedule_tiles function
tile_lib.schedule_tiles.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_int]
tile_lib.schedule_tiles.restype = ctypes.POINTER(ctypes.c_int)

# Example viewport data (as a 3D direction vector)
view_direction = (ctypes.c_float * 3)(0.0, 1.0, 0.0)

num_rows = 4
num_cols = 6

tiles_to_subscribe = tile_lib.schedule_tiles(view_direction, num_rows, num_cols)

# Multicast group address (for tiles)
MCAST_GRP = "ff02::1"# change to the multicast address
BASE_PORT = 0  # change to the base port number

# Function to subscribe to a multicast group on a specific port
def subscribe_to_tile(tile_index):
    port = BASE_PORT + tile_index
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Allow multiple sockets to use the same port number
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind to the multicast address and port
    sock.bind(('', port))

    # Join the multicast group on a specific interface
    group_bin = socket.inet_pton(socket.AF_INET6, MCAST_GRP)
    mreq = group_bin + struct.pack('@I', 0)  # Interface 0 for default

    # Tell the kernel to add us to the multicast group
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

    print(f"Subscribed to tile {tile_index} on port {port}")

    # Now this socket will receive data sent to the multicast group on this port
    return sock

# Subscribe to each tile returned by the C function
subscribed_sockets = []
for tile_index in tiles_to_subscribe:
    if tile_index >= 0:  # Make sure the tile index is valid
        subscribed_sockets.append(subscribe_to_tile(tile_index))

try:
    while True:
        for sock in subscribed_sockets:
            data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            print(f"Received data from {addr}: {data}")
except KeyboardInterrupt:
    print("Unsubscribing from tiles and exiting...")
