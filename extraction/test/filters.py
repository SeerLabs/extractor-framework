import extraction.runnables as runnables

class FilterWithoutDeps(runnables.Filter):
   def filter(self, data, dep_results):
      return True

class FilterWithDeps(runnables.Filter):
   @staticmethod
   def dependencies():
      return [FilterWithoutDeps]

   def filter(self, data, dep_results):
      return True

class PassFilter(runnables.Filter):
   def filter(self, data, dep_results):
      return True

class FailFilter(runnables.Filter):
   def filter(self, data, dep_results):
      return False


