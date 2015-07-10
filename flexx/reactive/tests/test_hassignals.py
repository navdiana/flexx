""" Test how signals behave on classes.
"""

from pytest import raises
from flexx.util.testing import run_tests_if_main

from flexx.reactive import HasSignals, input, signal, react, Signal


def test_signals_on_classes_are_descriptors():
    
    shown = []
    
    class Test(HasSignals):
        
        @input
        def title(v=''):
            return str(v)
        
        @react('title')
        def show_title1(v=''):
            shown.append(v)
        
        @react('title')
        def show_title2(self, v=''):
            shown.append(v)
    
    
    assert len(shown) == 0
    assert Test.title.not_connected
    assert Test.show_title1.not_connected
    assert Test.show_title2.not_connected
    
    t = Test()
    assert len(shown) == 2


def test_hassignals_without_self():
    
    title_lengths = []
    
    class Test(HasSignals):
        
        @input
        def title(v=''):
            return str(v)
        
        @signal('title')
        def title_len(v):
            return len(v)
        
        @react('title_len')
        def show_title(v):
            title_lengths.append(v)
    
    t = Test()
    
    assert set(t.__signals__) == set(['title', 'title_len', 'show_title'])
    
    assert len(title_lengths) == 1
    assert title_lengths[-1] == 0
    
    t.title('foo')
    assert len(title_lengths) == 2
    assert title_lengths[-1] == 3


def test_hassignals_with_self():
    
    title_lengths = []
    
    class Test(HasSignals):
        
        @input
        def title(self, v=''):
            return str(v)
        
        @signal('title')
        def title_len(self, v):
            return len(v)
        
        @react('title_len')
        def show_title(self, v):
            title_lengths.append(v)
    
    t = Test()
    
    assert set(t.__signals__) == set(['title', 'title_len', 'show_title'])
    
    assert len(title_lengths) == 1
    assert title_lengths[-1] == 0
    
    t.title('foo')
    assert len(title_lengths) == 2
    assert title_lengths[-1] == 3


def test_anyclass():
    
    title_lengths = []
    
    class Test(object):
        
        @input
        def title(self, v=''):
            return str(v)
        
        @signal('title')
        def title_len(self, v):
            return len(v)
        
        @react('title_len')
        def show_title(self, v):
            title_lengths.append(v)
    
    t = Test()
    
    assert not hasattr(t, '__signals__')
    
    # No signals instances have been created yet
    assert len(title_lengths) == 0
    
    t.show_title.connect(False)
    
    # Upstream signals do not yet exist
    assert len(title_lengths) == 0
    
    # Initialize the signals for real
    t.title
    t.title_len.connect()
    t.show_title.connect()
    
    assert len(title_lengths) == 1  # class signal does not fire, because it sees self arg
    assert title_lengths[-1] == 0
    
    t.title('foo')
    assert len(title_lengths) == 2
    assert title_lengths[-1] == 3


def test_connection_locals1():
    
    class Test(HasSignals):
        
        @signal('title')
        def title_len(self, v):
            return len(v)
    
    t = Test()
    assert t.title_len.not_connected
    
    @input
    def title(v=''):
        return str(v)
    
    t.connect_signals()
    assert not t.title_len.not_connected
    assert t.title_len() == 0
    
    title('foo')
    assert t.title_len() == 3


def test_connection_locals2():
    
    class Test(HasSignals):
        @signal('title')
        def title_len(self, v):
            return len(v)
    
    def create_instance():
        @input
        def title(v=''):
            return str(v)
        return Test()
    
    # The frame to look for "title" is relative to the clas def, not the instance
    t = create_instance()
    assert t.title_len.not_connected


def test_func_name():
    # Do not allow weird names, though not recommended
    # todo: now that we have a metaclass, we can allow it!
    
    with raises(RuntimeError):
        class Test(HasSignals):
            s1 = Signal(lambda x: x, [])
    
    with raises(RuntimeError):
        class Test(HasSignals):
            s2 = Signal(float, [])


def test_props():
    from flexx.reactive.reactive import prop
    title_lengths = []
    
    class Test(HasSignals):
        
        @prop
        def title(self, v=''):
            return str(v)
        
        @signal('title')
        def title_len(self, v):
            return len(v)
        
        @react('title_len')
        def show_title(self, v):
            title_lengths.append(v)
    
    t = Test()
    
    assert set(t.__signals__) == set(['title', 'title_len', 'show_title'])
    
    assert len(title_lengths) == 1
    assert title_lengths[-1] == 0
    
    t.title = 'foo'
    assert len(title_lengths) == 2
    assert title_lengths[-1] == 3


run_tests_if_main()