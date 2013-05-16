from ama import Asker, Question

questions = u'{"status": ["the status of the system", "1, 2\\nor 3", "string", 1, ["1","2","3"]]}'

def test_Question():
    q = Question('key', 'label')
    assert q.key == 'key'
    assert q.label == 'label'
    assert q.type == 'str'
    assert q.default is None
    assert q.help_text == ''
    assert q.validator is None
    assert len(q.depends_on) == 0

def test_Asker_dependencies():
    asker = Asker()
    d = asker._find_dependencies('{wally}and{dave}')
    
    assert d == ['wally', 'dave']
    
if __name__ == '__main__':
    test_Question()
    test_Asker_dependencies()
    