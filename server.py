import socket , selectors
import random

MSG_BLOCK_LEN   = 2048
BOARD_DIM     = 16
GRID_DIM      = 60

# Gameplay related variables
plyr_count = 0
conns = [None, None, None, None]
names = ['', '', '', '']
moves = [0, 0, 0, 0]

# Function to accept new clients
def accept():

    global plyr_count

    conn, addr = master_sock.accept()
    conns[plyr_count] = conn

    print( 'New connection from,', addr )

    socket_manager.register( conn, selectors.EVENT_READ, plyr_count )
    plyr_count += 1

def accept_name( _id ):
    msg = conns[_id].recv( MSG_BLOCK_LEN ).decode()
    msg = msg.split(';')
    names[_id] = msg[1].strip()
    print(_id, names[_id])

def start_game():
    msg = '0;' + (';'.join( names ))
    print(msg)
    for conn in conns: conn.send( msg.encode('utf-8') )

# Start server
my_ip = '127.0.0.1'
my_port = 8080

master_sock = socket.socket()
socket_manager = selectors.DefaultSelector()

master_sock.bind( (my_ip, my_port) )
master_sock.listen()
master_sock.setblocking( False )

socket_manager.register( master_sock, selectors.EVENT_READ, -1 )

# Main loop
running = True
game_start = False

print('Waiting for players to join')

while not game_start:

    for key, mask in socket_manager.select( timeout = 0.025 ):

        if( key.data < 0 ):
            accept()

        else:
            accept_name( key.data )
            if( plyr_count >= 4 ):
                start_game()
                game_start = True
                break

print('Starting game')

while game_start:

    for key, mask in socket_manager.select( timeout = 0.025 ):
        who = key.data
        big_msg = conns[who].recv(MSG_BLOCK_LEN).decode()
        big_msg = big_msg.split('\n')

        for msg in big_msg:
            if( len(msg) <= 0 ): continue

            msg = msg.split(';')
            print(msg)

            if( msg[0] == '1' ): # Piece moved
                # (1;piece;x;y)
                # (2;who;piece;x;y)
                send_back = '2;' + str( who ) + ';' + msg[1] + ';' + ';'.join( msg[2:] ) + '\n'
                for i in range( 4 ):
                    if( i == who ): continue
                    conns[i].send( send_back.encode('utf-8') )

            elif( msg[0] == '2' ): # Square blocked
                pass

            elif( msg[0] == '3' ): # Time state saved/unsaved
                # (3;0/1)
                # (4;who;what)
                send_back = '4;' + str( who ) + ';' + msg[1] + '\n'
                for i in range( 4 ):
                    if( i == who ): continue
                    conns[i].send( send_back.encode('utf-8') )

            elif( msg[0] == '4' ): # Client saying decrement treasure
                #(4;who)
                #(3;who)
                send_back = '3;' + msg[1] + '\n'
                for i in range( 4 ):
                    if( i == who ): continue
                    conns[i].send( send_back.encode('utf-8') )

