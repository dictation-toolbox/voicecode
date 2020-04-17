import string
import unittest
import debug

class TestCaseWithHelpers(unittest.TestCase):
    
    
    def __init__(self, name):
        unittest.TestCase.__init__(self, name)
    
    def assert_equals(self, expected, got, mess):
        mess = mess + ("\n   Expected : %s\n   Got      : %s\n" % (expected, got))
        self.assert_(expected == got, mess)

    def assert_string_contains(self, pattern, the_string, mess=''):
        self.assert_(string.find(the_string, pattern) != -1, 
                     mess + "\nSubstring: '%s' was not found in string: '%s'" % (pattern, the_string))
        

    def assert_sequences_have_same_content(self, expected, got, mess):
        """Use this to compare long lists, instead of just doing:
        
            assert(exepcted == got, ...)
            
        In case of a discrepancy, assert_sequences_have_same_content will tell you
        the index of the first entry that differs, so you won't have to scan two
        long lists visually.
        """
        display_both_lists_mess = \
           "\nExpected list:\n   %s\nGot list:\n   %s" % (repr(expected), repr(got))
        
        if len(expected) != len(got):  
           self.fail(mess + "\nExpeted sequence of length %s, but got sequence of length %s" 
                     % (len(expected), len(got)) + \
                     display_both_lists_mess)

        for ii in range(len(expected)):
           if expected[ii] != got[ii]:
              self.fail(mess + "\nItem at position %s was wrong. Expected '%s', but got '%s'" \
                     % (ii, expected[ii], got[ii]))
           
