# Extraction Framework #

## Using the framework ##

Example usage:

```python
# import require modules
import extraction.runnables as runnables
from extraction.core import ExtractionRunner

# define extractors and filters
class HasContentFilter(runnables.Filter):
   # All runnable classes and subclasses should specify their dependencies
   dependencies = []

   def filter(self, data, dependencyResults):
      return len(data) > 0

class TrimmedTextExtractor(runnables.Extractor):
   # only will be run in all filters in dependencies pass
   dependecies = [HasContentFilter]

   def extract(self, data, dependencyResults):
      return data[:-1]

# Create and run the whole extraction process
runner = ExtractionRunner()
runner.add_filter(HasContentFilter)
runner.add_extractor(TrimmedTextExtractor)

xmlResults = runner.runFromFile('/path/to/pdf')



## Running the unittests ##

Run, from the project root directory:

    python -m extraction.test.__main__

If using Python 2.7 you can run more simply:

    python -m extraction.test
