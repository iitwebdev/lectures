"""
Setup your Routes options here
"""
import os
from routes import Mapper

def make_map(global_conf={}, app_conf={}):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    map = Mapper(directory=os.path.join(root_path, 'controllers'))
    
    # This route handles displaying the error page and graphics used in the 404/500
    # error pages. It should likely stay at the top to ensure that the error page is
    # displayed properly.
    map.connect('*url', conditions=dict(function=show_data))
    map.connect('error/:action/:id', controller='error')
    
    # Define your routes. The more specific and detailed routes should be defined first,
    # so they may take precedent over the more generic routes. For more information, refer
    # to the routes manual @ http://routes.groovie.org/docs/
    map.connect(':controller/:action/:id')
    map.connect(':controller/:action')
    map.connect('/', controller='group_index',
                conditions=dict(function=lambda e, match: e.get('olpctag.show_group_index')))
    map.connect('/', controller='index')
    map.connect('/info/*uri', controller='info')
    map.connect('*url', controller='template', action='view')

    return map


def show_data(environ, match):
    print 'Incoming: %(SCRIPT_NAME)r/%(PATH_INFO)r' % environ
    print 'Match:', repr(match), environ.get('olpctag.show_group_index')
    return False
