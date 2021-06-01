# Blocking a square is considered a move
# Moving a piece is considered a move
# If a treasure was decremented, then the previous move is not to be counted
# If a state was reversed, then the previous moves are not to be considered moves
# The last token in every message is whether it was a move or not

import socket , selectors
import random

MSG_BLOCK_LEN   = 2048
BOARD_DIM     = 12
GRID_DIM      = 54

# Gameplay related variables
plyr_count = 0
conns = [None, None, None, None]
names = ['', '', '', '']
moves = [0, 0, 0, 0]

blocked = [[], [], [], []]

def tokenize( *args ):
    msg = str( args[0] )
    for i in range( len( args ) - 1 ):
        msg += ';' + str( args[i + 1] )
    msg += '\n'
    return msg

def send_everyone( _msg ):
    global conns

    for i in range( 4 ):
        conns[i].send( _msg.encode('utf-8') )

def send_rest( _msg ,_sender ):
    global conns

    for i in range( 4 ):
        if( i == _sender ): continue
        conns[i].send( _msg.encode('utf-8') )

# Function to check and remove blocked positions of a player
def remove_blocked( _id ):
    global conns, blocked, moves

    moves[ _id ] += 1
    while( len(blocked[who]) ):
        if( moves[_id] - blocked[_id][0][2] < 4 ):
            break

        send_back = '1;' + str( _id ) + ';' + str( blocked[who][0][0] ) + ';' + str( blocked[who][0][1] ) + ';' + '0' + '\n'
        send_everyone( send_back )
        del blocked[who][0]

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

# Start server
my_ip = ''
my_port = 48900

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
                send_back = '0;' + (';'.join( names ))
                send_everyone( send_back )
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

            if( msg[0] == '1' ): # Piece moved
                # (1;piece;x;y;move)    (2;who;piece;x;y)
                send_back = tokenize( 2, who, msg[1], msg[2], msg[3] )
                # send_back = '2;' + str( who ) + ';' + msg[1] + ';' + ';'.join( msg[2:] ) + '\n'
                send_rest( send_back, who )

                if( msg[-1] == '1' ): # This needs to be counted as move
                    remove_blocked( who )

            elif( msg[0] == '2' ): # Square blocked
                # (2;x;y)   (1;who;x;y;what)

                send_back = tokenize( 1, who, msg[1], msg[2], 1 )
                # send_back = '1;' + str( who ) + ';' + msg[1] + ';' + msg[2] + ';' + '1' + '\n'

                blocked[who].append( [int( msg[1] ), int( msg[2] ), moves[who]] )

                for i in range( 4 ):
                    if( i == who ): continue
                    conns[i].send( send_back.encode('utf-8') )

                if( msg[-1] == '1' ): # This needs to be counted as move
                    remove_blocked( who )

            elif( msg[0] == '3' ): # Time state saved/unsaved
                # (3;0/1)   (4;who;what)
                send_back = tokenize( 4, who, msg[1] )
                # send_back = '4;' + str( who ) + ';' + msg[1] + '\n'
                send_rest( send_back, who )

                if( msg[-1] == '1' ): # This needs to be counted as move
                    remove_blocked( who )

            elif( msg[0] == '4' ): # Client saying decrement treasure
                # (4;who)   (3;who)
                send_back = tokenize( 3, msg[1] )
                # send_back = '3;' + msg[1] + '\n'
                send_rest( send_back, who )
