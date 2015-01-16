import unittest
import extraction.runnables as runnables

class FilterWithoutDeps(runnables.Filter):
   def filter(self, data, dependencyResults):
      return True

class FilterWithDeps(runnables.Filter):
   @staticmethod
   def dependencies():
      return [FilterWithoutDeps]

   def filter(self, data, dependencyResults):
      return True

class TrueFilter(runnables.Filter):
   def filter(self, data, dependencyResults):
      return True

class FalseFilter(runnables.Filter):
   def filter(self, data, dependencyResults):
      return False


class TestRunnables(unittest.TestCase):
   def setUp(self):
      pass

   def test_defining_dependencies(self):
      noDeps = FilterWithoutDeps()
      hasDeps = FilterWithDeps()

      self.assertTrue(hasattr(FilterWithoutDeps, 'dependencies'))
      self.assertEqual(len(FilterWithoutDeps.dependencies()), 0)
      self.assertEqual(len(FilterWithDeps.dependencies()), 1)
      self.assertTrue(FilterWithoutDeps in FilterWithDeps.dependencies())

   def test_filter_method_gets_run(self):
      self.assertTrue(TrueFilter().run("some_data", {}))
      self.assertFalse(FalseFilter().run("some_data", {}))

