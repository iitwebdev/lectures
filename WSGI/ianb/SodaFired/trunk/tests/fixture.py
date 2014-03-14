import os
from paste.deploy import loadapp, appconfig
from paste.fixture import TestApp
import sqlobject
from sodafired import db
from sqlobject.util import csvimport

__all__ = ['setup_module', 'db']

config_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'docs')

def setup_module(mod):
    wsgiapp = loadapp('config:devel_config.ini#test',
                      relative_to=config_dir)
    conf = appconfig('config:devel_config.ini#test',
                     relative_to=config_dir)
    app = TestApp(wsgiapp)
    mod.app = app
    mod.wsgiapp = wsgiapp
    sqlobject.sqlhub.processConnection = sqlobject.connectionForURI(
        conf['database'])
    def reset_db():
        db.init_db(True)
        dbobjs = database_reset()
        mod.dbobjs = dbobjs
        return dbobjs
    mod.reset_db = reset_db
    reset_db()

def database_reset():
    if hasattr(db, 'create_basic_data'):
        db.create_basic_data()
    data = csvimport.load_csv_from_directory(
        os.path.join(os.path.dirname(__file__), 'dbdata'))
    dbobjs = csvimport.create_data(data, db)
    return dbobjs
    
if __name__ == '__main__':
    import sys
    if sys.argv[1:]:
        database = sys.argv[1]
    else:
        conf = appconfig('config:devel_config.ini#test',
                         relative_to=config_dir)
        database = conf['database']
    sqlobject.sqlhub.processConnection = sqlobject.connectionForURI(
        database)
    db.init_db(True)
    database_reset()
    
