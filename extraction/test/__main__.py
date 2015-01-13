import unittest

from extraction.test import test_all

tests = unittest.TestLoader()
test0 = tests.loadTestsFromModule(test_all)

all_tests = unittest.TestSuite([test0])

if __name__ == '__main__':
   unittest.TextTestRunner().run(all_tests)
