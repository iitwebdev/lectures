from sqlobject import *

hub = sqlhub

class Piece(SQLObject):

    title = StringCol(notNull=True)
    link = StringCol(alternateID=True)
    description = StringCol()
    price = CurrencyCol()
    inventory = IntCol(notNull=True, default=0)
    active = BoolCol(notNull=True, default=True)

class PieceTags(SQLObject):

    piece = ForeignKey('Piece', cascade=True)
    tag = StringCol(notNull=True)

class Section(SQLObject):

    title = StringCol(notNull=True)
    link = StringCol(alternateID=True)
    description = StringCol()
    tag = StringCol()

def init_db(reset=False):
    for table in Piece, PieceTags, Section:
        table.createTable(ifNotExists=True)
        if reset:
            table.clearTable()
    
