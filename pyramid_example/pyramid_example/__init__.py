from pyramid.config import Configurator
from pyramid.response import Response
from sqlalchemy import engine_from_config

from .models import Base, DBSession, MyModel


def goodbye(request):
    return Response('Goodbye world!')


def includeme(config):
    config.add_route('goodbye', '/goodbye')
    config.add_view(goodbye, route_name='goodbye')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)

    # pyramid_jinja2 configuration
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("pyramid_example:templates")

    # SACRUD
    config.include('sacrud.pyramid_ext', route_prefix='/admin')
    settings = config.registry.settings
    settings['sacrud.models'] = {'Test': [MyModel], }

    # include view
    includeme(config)

    # include from other model
    config.include('pyramid_example.my_super_includeme')

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    return config.make_wsgi_app()
