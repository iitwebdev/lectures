from pyramid.response import Response


def super_func(request):
    return Response("I'm super includeme!")


def includeme(config):
    config.add_route('super', '/super_includeme')
    config.add_view(super_func, route_name='super')
