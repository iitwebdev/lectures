import poorman
import os
from sqlobject.wsgi_middleware import make_middleware

project = poorman.Project(
    'sodafired', default_template_type='cheetah')

project.add_middleware(make_middleware)

project.connect('/pieces/:name',
                controller='piece',
                action='view')

project.connect('/sections/:name',
                controller='section',
                action='view')

project.connect('/admin/:type/:object',
                controller='admin',
                action=':type',
                post_append='_submit')

project.connect('/admin/:type/',
                controller='admin',
                action=':type',
                action_append='_index')

project.connect('/catwalk/*path_info',
                path_info='',
                controller='egg:CherryPaste#catwalk',
                model='sodafired.db')

static_dir = os.path.join(os.path.dirname(__file__), 'static')
project.connect('/static/*path_info',
                path_info='',
                controller='egg:Paste#static',
                document_root=static_dir)

controller = project.controller
decode = poorman.decode
