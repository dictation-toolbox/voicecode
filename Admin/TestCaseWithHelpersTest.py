import TestCaseWithHelpers
import debug


class TestCaseWithHelpersTest(TestCaseWithHelpers.TestCaseWithHelpers):
    
    def __init__(self, name):
       TestCaseWithHelpers.TestCaseWithHelpers.__init__(self, name)
       self.nevermind = "Nevermind, this test is supposed to fail."
       
    def should_have_failed_earlier(self):
       fail("ERROR: this test should have failed earlier than here.")
    
    def test_bad_length_in_assert_sequences_have_same_content(self):
        self.assert_sequences_have_same_content([], [1, 2], self.nevermind)
        self.should_have_failed_earlier()
        
    def test_different_first_item_in_assert_sequences_have_same_content(self):
        self.assert_sequences_have_same_content(['hello', 'world'], ['hello', 'universe'],
                                                self.nevermind)
        self.should_have_failed_earlier()
        
    def test_different_last_item_in_assert_sequences_have_same_content(self):
        self.assert_sequences_have_same_content(['hello', 'world'], ['hi', 'world'],
                                                self.nevermind)
        self.should_have_failed_earlier()        
        
    def test_different_middle_item_in_assert_sequences_have_same_content(self):
        self.assert_sequences_have_same_content(['hello', 'beautiful', 'world'], 
                                                ['hello', 'wonderful', 'world'],
                                                self.nevermind)
        self.should_have_failed_earlier()        
        
