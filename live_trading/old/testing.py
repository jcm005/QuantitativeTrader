from unittest import TestCase
from garbage import StreamTrader
#import a function you wanna test
class functionTestCase(TestCase):
    '''Test for any function'''

    def first_test(self):
        '''one of many test'''
        # execut function you wanna test
        variable = 'the return of the function you wanna test'
        self.assertEqual(variable,'put what the answer should be')

    def setUp(self) -> None:
        ''' the init of testing
        it creates a survey instance and it creates a list of responses'''
    unittest.main()

