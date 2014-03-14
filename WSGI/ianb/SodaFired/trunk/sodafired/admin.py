from db import *
from web import controller, decode

default_piece = {
    'description': """\
<b>Dimensions:</b>
"""}

@controller()
@decode(obj=(Piece.get, 'new'))
def piece(req, obj):
    if obj == 'new':
        defaults = default_piece
    else:
        defaults = dict(
            title=obj.title,
            link=obj.link,
            description=obj.description,
            price=obj.price,
            inventory=obj.inventory,
            active=obj.active)
    defaults.update(req.fields)
    return req.render()

@controller()
@decode(obj=(Piece.get, 'new'),
        inventory=int, price=float)
def piece_submit(req, obj, **kw):
    if obj == 'new':
        Piece(**kw)
        req.flash('Piece %s created', obj.title)
    else:
        obj.set(**kw)
        req.flash('Piece %s updated', obj.title)
    req.redirect_self()
