from asker import Asker, TkAsker

questions = u'{"status": ["the status of the system", "1, 2\\nor 3", "string", 1, ["1","2","3"]]}'

def test_Asker_split_line():
    asker = Asker()
    asker.loads(questions)

def test_TkAsker():
    asker = TkAsker()
    asker.loads(questions)
    
if __name__ == '__main__':
    test_Asker_split_line()
    test_TkAsker()
    