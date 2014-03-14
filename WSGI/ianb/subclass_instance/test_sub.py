import sub

def test_inst():
    inst = sub.Subclassable(a=1, b=2)
    print inst
    assert inst.a == 1
    assert inst.b == 2
    class inst2(inst):
        a = 2
        c = 3
    print inst2
    assert isinstance(inst2, inst.__class__)
    assert inst2.a == 2
    assert inst2.b == 2
    assert inst2.c == 3
