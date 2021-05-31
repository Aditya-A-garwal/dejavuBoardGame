BOARD_DIM     = 12
GRID_DIM      = 54

def BIT1( _x ):
    if( _x & 1 ): return True
    return False

def BIT2( _x ):
    if( _x & 2 ): return True
    return False

def BIT3( _x ):
    if( _x & 4 ): return True
    return False

def BIT4( _x ):
    if( _x & 8 ): return True
    return False

def pos( _x ):
    return 1 + _x * (GRID_DIM + 1)

def tpos( _t ):
    return [ pos( _t[0] ), pos( _t[1] ) ]

def is_valid( _lst2, _lst1 ):
    for i in range( 4 ):
        if( _lst2 in _lst1[i] ): return False
    return True

def is_validb( _lst2, _lst1, my_id ):
    for i in range( 4 ):
        if( i == my_id ): continue
        if( _lst2 in _lst1[i] ): return False
    return True

BITS = [BIT1, BIT2, BIT3, BIT4]