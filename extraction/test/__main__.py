import unittest

from extraction.test import test_core, test_runnables, test_xmltodict, test_dicttoxml

tests = unittest.TestLoader()
test_arr = []
test_arr.append(tests.loadTestsFromModule(test_core))
test_arr.append(tests.loadTestsFromModule(test_runnables))
test_arr.append(tests.loadTestsFromModule(test_xmltodict))
test_arr.append(tests.loadTestsFromModule(test_dicttoxml))

all_tests = unittest.TestSuite(test_arr)

if __name__ == '__main__':
   unittest.TextTestRunner().run(all_tests)
