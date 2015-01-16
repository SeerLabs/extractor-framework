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


