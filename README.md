# Extraction Framework #

## Prerequisites ##
* Python 2.6 (or Python 2.7 should work probably)
* [xmltodict package](https://github.com/martinblech/xmltodict)
* [defusedxml package](https://pypi.python.org/pypi/defusedxml)
* [subprocess32 package](https://pypi.python.org/pypi/subprocess32)

## Installation ##
Clone this repo to your local machine anywhere
From the project root directory, run:

    python setup.py install --user

(The --user option is optional, I just like to 
install packages only for my user account personally)

## Using the framework ##

#### Creating Filters and Extractors ####

```
#!python

# import needed classes from extraction.runnable module
from extraction.runnables import Extractor, Filter, RunnableError, ExtractionResult
import xml.etree.ElementTree as ET
import extraction.utils as utils

# every extractor/filter is defined in its own class
# extractors must inherit from Extractor
class TextExtractor(Extractor):
   # if the extractor depends on the results of other extractors or filters
   # it must override the static dependencies method
   @staticmethod
   def dependencies():
      return [EnglishFilter]

   # extractors must override the extract method
   # this is where the main logic goes
   # the data argument contains the original data that the extraction runner started with
   # any results from dependencies are placed in the dep_results argument
   def extract(self, data, dep_results):
      # if something unexpected happens, a RunnableError should be raised
      if some_module.is_bad(data):
         raise RunnableError('Data in improper format')
      else
         text_part_1 = some_module.get_some_text(data)
         text_part_2 = some_module.get_some_text(data)
         file_path_1 = 'text-file-1.txt'
         file_path_2 = 'text-file-2.txt'
         
         root = ET.Element('text-files')
         ele1 = ET.SubElement(root, 'file')
         ele1.text = file_path_1
         ele2 = ET.SubElement(root, 'file')
         ele2.text = file_path_2

         files = { file_path_1: text_part_1, file_path_2: text_part_2 }

         # the extract method should return an ExtractionResult object
         # it has a mandatory xml_result field which should be a xml.etree.ElementTree.element object
         # the files parameter is optional but if supplied is a dictionary such that dict[file_name] = file_contents
         # the xml result will be written to the output directory of the whole extraction process as well as the files in files
         result = ExtractionResult(xml_result=root, files=files)
         return result

# filters extend the Filter class
class EnglishFilter(Filter):
   # they may also declare dependencies if desired
   # this filter has no dependencies

   # Filters must override the filter method
   # this is where their main logic goes
   def filter(self, data, dep_results):
      # filters should return a boolean: True for passing and False for failing
      # like extractors, they may also raise a RunnableError if something goes wrong
      return ' the ' in data

```

A note on writing extractors:
Extractors that return results of the same format should extend a common subclass of Extractor.
This way, classes can define their dependencies to rely on that common subclass.
A quick stub example:

```python

# Interface extractor
# Any extractor extending this class should return an xml document defined by XML DTD EmailExtraction.dtd
class EmailExtractor(Extractor):
   def extract(self, data, dep_results):
      raise NotImplementedError('This is an abstract class!')

class AwkEmailExtractor(EmailExtractor):
   def extract(self, data, dep_results):
      ...

class GrepEmailExtractor(EmailExtractor):
   def extract(self, data, dep_results):
      ...

class WebdomainExtractor(Extractor):
   @staticmethod
   def dependencies():
      return [EmailExtractor]

   def extract(self, data, dep_results):
      ...
```

In this example above, either `AwkEmailExtractor` *or* GrepEmailExtractor can be used
and WebdomainExtractor will still work. This is important because it allows us to easily
substitute in and out extractors that work differently but return data in the same format


## Sample Framework Usage ##
For another example of usage, see extraction/test/sample.py

Or, from the project root, you can run:

    python -m extraction.test.sample


## Running the unittests ##

Run, from the project root directory:

    python -m extraction.test.__main__

If using Python 2.7 you can run more simply:

    python -m extraction.test
