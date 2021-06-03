import os
os.system('pip install --user pygame')

import pygame , pygame.freetype
import socket , selectors
import colors , BIT
import random

MSG_BLOCK_LEN = 2048
BOARD_DIM     = 12
GRID_DIM      = 54

name = input('Enter name: ').strip()
plyr_count = 4

pygame.init()
pygame.freetype.init()

# Start the window
display_sz  = [900, 675]
screen      = pygame.display.set_mode( display_sz , pygame.RESIZABLE )
pygame.display.set_caption( name )

# Mouse pos
mouse_pos   = [0, 0]

# Address of server
serv_addr   = (input('Enter Server IP: ').strip(), 48900)

my_sock     = socket.socket()
sock_mngr   = selectors.DefaultSelector()

# Connect to the server and send own name
my_sock.connect( serv_addr )
my_sock.send( ('0;{}'.format( name )).encode( 'utf-8' ) )

# Add socket to socket manager for async operation
my_sock.setblocking( False )
sock_mngr.register( my_sock, selectors.EVENT_READ, 1 )

# Start positions of all pieces and states of all treasures
treasure_pos= [[0, BOARD_DIM - 1], [0, 0], [BOARD_DIM - 1 ,0], [BOARD_DIM - 1, BOARD_DIM - 1]]
plyr1_pos   = [[0, BOARD_DIM - 2], [1, BOARD_DIM - 1], [1, BOARD_DIM - 2]]
plyr2_pos   = [[0, 1], [1, 0], [1, 1]]
plyr3_pos   = [[BOARD_DIM - 2, 0], [BOARD_DIM - 1, 1], [BOARD_DIM - 2, 1]]
plyr4_pos   = [[BOARD_DIM - 2, BOARD_DIM - 1], [BOARD_DIM - 1, BOARD_DIM - 2], [BOARD_DIM - 2, BOARD_DIM - 2]]

init_pos    = None

pos         = [plyr1_pos, plyr2_pos, plyr3_pos, plyr4_pos]
pos_save    = None

blocked_pos = [[], [], [], []]

legal_show  = False
legal_moves = None
which_piece = -1

# Names of all the players along with a count of their treasures
my_id       = 0
names       = ['plyr 1', 'plyr 2', 'plyr 3', 'plyr 4']
points      = [4, 4, 4, 4]
time_states = [0, 0, 0, 0]

# Game board
board       =  [
    [0b0000, 0b0010, 0b0001, 0b0001, 0b0101, 0b1010, 0b0101, 0b0101, 0b1000, 0b0001, 0b1000, 0b0000],
    [0b0010, 0b0101, 0b0001, 0b0101, 0b0110, 0b1100, 0b0001, 0b0100, 0b0001, 0b1011, 0b0101, 0b1000],
    [0b0100, 0b1011, 0b1000, 0b0001, 0b1001, 0b0011, 0b1001, 0b0100, 0b1010, 0b0010, 0b0100, 0b1010],
    [0b1000, 0b0100, 0b0001, 0b1110, 0b1111, 0b0011, 0b0100, 0b1001, 0b1000, 0b0100, 0b1110, 0b1000],
    [0b1010, 0b0101, 0b1010, 0b1010, 0b0011, 0b1001, 0b0110, 0b1110, 0b1111, 0b0100, 0b1010, 0b1000],
    [0b0001, 0b1000, 0b0001, 0b0100, 0b1000, 0b0100, 0b0001, 0b0010, 0b1111, 0b0101, 0b0001, 0b0100],
    [0b0100, 0b0101, 0b0100, 0b1111, 0b0010, 0b0100, 0b0001, 0b1000, 0b0001, 0b1001, 0b0100, 0b0001],
    [0b0010, 0b1100, 0b0001, 0b1001, 0b1100, 0b0011, 0b0110, 0b1110, 0b0110, 0b1000, 0b0011, 0b1010],
    [0b0010, 0b1100, 0b0100, 0b1001, 0b0100, 0b1111, 0b0001, 0b1111, 0b0100, 0b1001, 0b0100, 0b0010],
    [0b0100, 0b1011, 0b1000, 0b0101, 0b0011, 0b1100, 0b0100, 0b0010, 0b0001, 0b1000, 0b1100, 0b1010],
    [0b1000, 0b0101, 0b0001, 0b0001, 0b1100, 0b0011, 0b1010, 0b1010, 0b1010, 0b1011, 0b0101, 0b0010],
    [0b0000, 0b1000, 0b0010, 0b1010, 0b0100, 0b1010, 0b0101, 0b0100, 0b1000, 0b0001, 0b0010, 0b0000]
]

# Load all textures
board_sz    = [ (GRID_DIM + 1) * BOARD_DIM + 1 , (GRID_DIM + 1) * BOARD_DIM + 1 ]
board_surf  = pygame.image.load( 'Resources/Board.png' )
place_mark  = pygame.image.load( 'Resources/validplace.png' )
place_mark  = pygame.transform.scale( place_mark, (GRID_DIM, GRID_DIM) )

lines       = ['Horizontal', 'LeftRise', 'Vertical', 'RightRise']
treasures   = ['', '', '', '']

plyr1_pawn  = ['', '']
plyr2_pawn  = ['', '']
plyr3_pawn  = ['', '']
plyr4_pawn  = ['', '']

pawns       = [plyr1_pawn, plyr2_pawn, plyr3_pawn, plyr4_pawn]

# Constants for faster access
board_offset = [ (display_sz[0] - board_sz[0])//2, (display_sz[1] - board_sz[1])//2 ]

for i in range( 4 ):

    lines[i]        = pygame.image.load( 'Resources/{}.png'.format( lines[i] ) )
    lines[i]        = pygame.transform.scale( lines[i], (GRID_DIM, GRID_DIM) )

    treasures[i]    = pygame.image.load( 'Resources/treasure{}.png'.format( i ) )
    treasures[i]    = pygame.transform.scale( treasures[i], (GRID_DIM, GRID_DIM) )

    pawns[i][0]     = pygame.image.load( 'Resources/soldier{}.png'.format( i ) )
    pawns[i][0]     = pygame.transform.scale( pawns[i][0] , (GRID_DIM, GRID_DIM) )

    pawns[i][1]     = pygame.image.load( 'Resources/builder{}.png'.format( i ) )
    pawns[i][1]     = pygame.transform.scale( pawns[i][1] , (GRID_DIM, GRID_DIM) )

# Render the arrows and treasures on the game board
for i in range( BOARD_DIM ):
    for j in range( BOARD_DIM ):
        coors = BIT.tpos( (i, j) )
        for k in range( 4 ):
            if( BIT.BITS[k]( board[i][j] ) ): board_surf.blit( lines[k], coors )

for i in range( 4 ):
    board_surf.blit( treasures[i], ( BIT.tpos( treasure_pos[i] ) ) )

# Main loop
running = True
game_start = False

while running:

    for event in pygame.event.get():

        if( event.type == pygame.QUIT ):
            running = False
            break
            #! We have to find a way to gracefully exit

        elif( event.type == pygame.VIDEORESIZE ):
            display_sz[0] = screen.get_width()
            display_sz[1] = screen.get_height()

            board_offset[0] = (display_sz[0] - board_sz[0])//2
            board_offset[1] = (display_sz[1] - board_sz[1])//2

        elif( event.type == pygame.KEYDOWN ):
            if( event.key == pygame.K_s):

                if( points[my_id] == 0 ): continue

                if( pos_save is None): # Save a new state
                    pos_save    = [[0, 0], [0, 0], [0, 0], []]
                    pos_save[0] = pos[my_id][0].copy()
                    pos_save[1] = pos[my_id][1].copy()
                    pos_save[2] = pos[my_id][2].copy()

                    pos_save[3] = blocked_pos[my_id].copy()
                    time_states[my_id] = 1

                    to_send = '3;1\n'
                    my_sock.send( to_send.encode('utf-8') )

                else:   # Go back to an old state
                    if( BIT.is_valid( pos_save[0], pos ) and BIT.is_validb( pos_save[0], blocked_pos, my_id ) ):
                        pos[my_id][0] = pos_save[0].copy()
                    if( BIT.is_valid( pos_save[1], pos ) and BIT.is_validb( pos_save[1], blocked_pos, my_id ) ):
                        pos[my_id][1] = pos_save[1].copy()
                    if( BIT.is_valid( pos_save[2], pos ) and BIT.is_validb( pos_save[2], blocked_pos, my_id ) ):
                        pos[my_id][2] = pos_save[2].copy()

                    for position in pos_save[3]:
                        flag = 1
                        for i in range( 4 ):
                            if( position in blocked_pos[i] ):
                                flag = 0
                                break
                        if( flag ):
                            blocked_pos[my_id].append( position )
                            to_send = '2;' + str( blocked_pos[my_id][-1][0] ) + ';' + str( blocked_pos[my_id][-1][1] ) + ';0\n'
                            my_sock.send( to_send.encode('utf-8') )

                    pos_save = None
                    time_states[my_id] = 0

                    to_send = '3;0\n'
                    my_sock.send( to_send.encode('utf-8') )

                    for i in range( 3 ):
                        to_send = '1;' + str( i ) + ';' + str( pos[my_id][i][0] ) + ';' + str( pos[my_id][i][1] ) + ';0\n'
                        my_sock.send( to_send.encode('utf-8') )

        elif( event.type == pygame.KEYUP ):
            pass

        elif( event.type == pygame.MOUSEBUTTONDOWN ):
            mouse_pos[0] = (pygame.mouse.get_pos()[0] - board_offset[0]) // (GRID_DIM + 1)
            mouse_pos[1] = (pygame.mouse.get_pos()[1] - board_offset[1]) // (GRID_DIM + 1)

            # Left click is either for moving or for showing legal moves
            if( event.button == 1 ):

                if( points[my_id] == 0 ): continue

                if( legal_show and mouse_pos in legal_moves ):
                    pos[my_id][which_piece][0]  = mouse_pos[0]
                    pos[my_id][which_piece][1]  = mouse_pos[1]

                    to_send = '1;' + str( which_piece ) + ';' + str( pos[my_id][which_piece][0] ) + ';' + str( pos[my_id][which_piece][1] ) + ';1\n'
                    my_sock.send( to_send.encode('utf-8') )

                    legal_show = False

                    treasure_taken = -1

                    try: treasure_taken = treasure_pos.index( pos[my_id][which_piece] )
                    except: pass

                    if( points[treasure_taken] <= 0 ): treasure_taken = -1

                    if( treasure_taken >= 0 ):
                        pos[my_id][which_piece] = init_pos[which_piece].copy()
                        points[treasure_taken] -= 1

                        to_send = '1;' + str( which_piece ) + ';' + str( init_pos[which_piece][0] ) + ';' + str( init_pos[which_piece][1] ) + ';0\n'
                        print(to_send)
                        my_sock.send( to_send.encode('utf-8') )

                        to_send = '4;' + str( treasure_taken ) + '\n'
                        my_sock.send( to_send.encode('utf-8') )

                else:
                    which_piece = -1

                    try: which_piece = pos[my_id].index( mouse_pos )
                    except: pass

                    if( which_piece < 0 ):
                        legal_show = False
                        legal_moves = None

                    else:
                        legal_show = True
                        legal_moves = []

                        x, y = pos[my_id][which_piece]
                        position = board[x][y]

                        if( BIT.BITS[0]( position ) ): # Horizontal
                            i = x + 1
                            while( i < BOARD_DIM ):
                                if( BIT.is_valid( [i, y], pos ) and BIT.is_validb( [i, y], blocked_pos, my_id ) ):
                                    legal_moves.append( [i, y] )
                                else:
                                    break
                                i += 1

                            i = x - 1
                            while( i >= 0 ):
                                if( BIT.is_valid( [i, y], pos ) and BIT.is_validb( [i, y], blocked_pos, my_id ) ):
                                    legal_moves.append( [i, y] )
                                else:
                                    break
                                i -= 1

                        if( BIT.BITS[1]( position ) ): # Left Rise
                            i, j = x - 1, y - 1
                            while( i >= 0 and j >= 0 ):
                                if( BIT.is_valid( [i, j], pos ) and BIT.is_validb( [i, j], blocked_pos, my_id ) ):
                                    legal_moves.append( [i, j] )
                                else:
                                    break
                                i -= 1; j -= 1

                            i, j = x + 1, y + 1
                            while( i < BOARD_DIM and j < BOARD_DIM ):
                                if( BIT.is_valid( [i, j], pos ) and BIT.is_validb( [i, j], blocked_pos, my_id ) ):
                                    legal_moves.append( [i, j] )
                                else:
                                    break
                                i += 1; j += 1

                        if( BIT.BITS[2]( position ) ): # Vertical
                            i = y + 1
                            while( i < BOARD_DIM ):
                                if( BIT.is_valid( [x, i], pos ) and BIT.is_validb( [x, i], blocked_pos, my_id ) ):
                                    legal_moves.append( [x, i] )
                                else:
                                    break
                                i += 1

                            i = y - 1
                            while( i >= 0 ):
                                if( BIT.is_valid( [x, i], pos ) and BIT.is_validb( [x, i], blocked_pos, my_id ) ):
                                    legal_moves.append( [x, i] )
                                else:
                                    break
                                i -= 1

                        if( BIT.BITS[3]( position ) ): # Right Rise
                            i, j = x+1, y-1
                            while( i < BOARD_DIM and j >= 0 ):
                                if( BIT.is_valid( [i, j], pos ) and BIT.is_validb( [i, j], blocked_pos, my_id ) ):
                                    legal_moves.append( [i, j] )
                                else:
                                    break
                                i += 1; j -= 1

                            i, j = x - 1, y + 1
                            while( i >= 0 and j < BOARD_DIM ):
                                if( BIT.is_valid( [i, j], pos ) and BIT.is_validb( [i, j], blocked_pos, my_id ) ):
                                    legal_moves.append( [i, j] )
                                else:
                                    break
                                i -= 1; j += 1

            # Right click is for blocking a square
            elif( event.button == 3 ):

                if( which_piece == 2 and mouse_pos in legal_moves ):
                    blocked_pos[my_id].append( mouse_pos.copy() )
                    legal_show = False

                    to_send = '2;' + str( blocked_pos[my_id][-1][0] ) + ';' + str( blocked_pos[my_id][-1][1] ) + ';1\n'
                    my_sock.send( to_send.encode('utf-8') )

        elif( event.type == pygame.MOUSEBUTTONUP ):
            pass

    for key, mask in sock_mngr.select( timeout = 0.025 ):

        big_msg = my_sock.recv( MSG_BLOCK_LEN ).decode()
        big_msg = big_msg.split( '\n' )

        for msg in big_msg:
            if( len(msg) <= 0 ): continue

            msg = msg.split( ';' )

            if( msg[0] == '0' ): # Server sending names
                names = msg[1:]
                my_id = names.index( name )

                init_pos = ['', '', '']
                init_pos[0] = pos[my_id][0].copy()
                init_pos[1] = pos[my_id][1].copy()
                init_pos[2] = pos[my_id][2].copy()

                game_start = True

            elif( msg[0] == '1' ): # Server sending un/block a square
                whom = int( msg[1] )
                where = msg[2:4]
                what = int( msg[4] )

                where[0], where[1] = int( where[0] ), int( where[1] )

                if ( what ): # Block
                    blocked_pos[whom].append( where )
                else: # unblock
                    blocked_pos[whom].remove( where )

            elif( msg[0] == '2' ): # Server sending move a piece

                whom = msg[1:3]
                new_pos = msg[3:]

                new_pos[0] = int( new_pos[0] )
                new_pos[1] = int( new_pos[1] )

                pos[int( whom[0] )][int( whom[1] )] = new_pos.copy()

            elif( msg[0] == '3' ): # Server sending decrement treasure
                who = int( msg[1] )

                points[who] -= 1
                if( points[who] <= 0 ):
                    pos[who][0] = [-1, -1]
                    pos[who][1] = [-1, -1]
                    pos[who][2] = [-1, -1]
                    plyr_count -= 1

            elif( msg[0] == '4' ): # Server sending someone has saved/unsaved a state
                who = int( msg[1] )
                what = int( msg[2] )

                time_states[who] = what

    # Fill the screen black
    screen.fill( colors.black )

    if game_start:

        # Calculate where to render the board and render it
        rect    = [ board_offset[0], board_offset[1] ]
        screen.blit( board_surf, rect )

        # Get the font and render the names of the players in their respective colors
        font    = pygame.freetype.SysFont( 'Consolas', 26, True )

        texts   = [ font.render( names[i] + ' x' + str( points[i] ) + ' T' * time_states[i] , colors.plyr_clrs[i] ) for i in range( 4 ) ]

        # Calculate where to place each player's name and render it
        for i in range( 4 ):
            text, rect = texts[i]

            x_offset = (board_offset[0] - text.get_width())//2
            if( i >= 2 ): x_offset += board_offset[0] + board_sz[0]

            y_offset = display_sz[1] - text.get_height() - 80
            if( i == 1 or i == 2 ): y_offset = 80

            screen.blit( text, (x_offset, y_offset) )

        # Render the player's pieces and blocked places
        for i in range( 4 ):

            if( points[i] <= 0 ): continue

            soldier_pos_1 = BIT.tpos( pos[i][0] )
            soldier_pos_2 = BIT.tpos( pos[i][1] )
            builder_pos_1 = BIT.tpos( pos[i][2] )

            for j in range( 2 ):
                soldier_pos_1[j] += board_offset[j]
                soldier_pos_2[j] += board_offset[j]
                builder_pos_1[j] += board_offset[j]

            screen.blit( pawns[i][0], soldier_pos_1 )
            screen.blit( pawns[i][0], soldier_pos_2 )
            screen.blit( pawns[i][1], builder_pos_1 )

            for block in blocked_pos[i]:
                blit_coors = BIT.tpos( block )
                blit_coors[0] += board_offset[0]
                blit_coors[1] += board_offset[1]

                screen.blit( treasures[i], blit_coors )

        # Render the player's legal moves if enabled
        if( legal_show ):
            x, y = pos[my_id][which_piece]
            position = board[x][y]

            for possible_move in legal_moves:
                blit_pos = BIT.tpos( possible_move )
                blit_pos[0] += board_offset[0]
                blit_pos[1] += board_offset[1]

                screen.blit( place_mark, blit_pos )

    else:

        # Get the rendered text (in white) and calculate where to render it
        font = pygame.freetype.SysFont( 'Consolas', 80, True )
        text, rect = font.render('WAITING FOR PLAYERS', colors.white )
        rect = [ (display_sz[0] - text.get_width())//2, (display_sz[1] - text.get_height())//2 ]

        screen.blit( text, rect )

    pygame.display.update()

pygame.display.quit()
pygame.quit()