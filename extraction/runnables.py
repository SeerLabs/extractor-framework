class Base(object):
   def __init__(self):
      pass

class Filter(Base):
   def filter(self, data, dependencyResults):
      return False

class Extractor(Base):
   def extract(self, data, dependencyResults):
      return 'TODO'
