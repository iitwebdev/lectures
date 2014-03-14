from db import *
from web import controller

@controller()
def view(req, name):
    piece = Piece.byLink(name)
    title = piece.title
    return req.render()
    
