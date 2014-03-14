from fixture import *

def test_app():
    res = app.get('/pieces/bowl')

def test_external():
    res = app.get('/static/stylesheet.css')
    res.mustcontain('font-family')
    #res = app.get('/catwalk/')
    #res.mustcontain('<html>')

def test_admin():
    res = app.get('/admin/piece/new')
    print res
    assert 0
