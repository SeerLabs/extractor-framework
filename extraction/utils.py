import subprocess32 as subprocess
import threading
import signal
import tempfile
import os

def external_process(process_args, input_data='', timeout=None):
   '''
   Pipes input_data via stdin to the process specified by process_args and returns the results

   Arguments:
      process_args -- passed directly to subprocess.Popen(), see there for more details
      input_data -- the data to pipe in via STDIN (optional)
      timeout -- number of seconds to time out the process after (optional)
        IF the process timesout, a subprocess32.TimeoutExpired exception will be raised

   Returns:
      (exit_status, stdout, stderr) -- a tuple of the exit status code and strings containing stdout and stderr data

   Examples:
      >>> external_process(['grep', 'Data'], input_data="Some String\nWith Data")
      (0, 'With Data\n', '')
   '''
   process = subprocess.Popen(process_args,
                              stdout=subprocess.PIPE,
                              stdin=subprocess.PIPE,
                              stderr=subprocess.PIPE)
   try:
      (stdout, stderr) =  process.communicate(input_data, timeout)
   except subprocess.TimeoutExpired as e:
      # cleanup process
      # see https://docs.python.org/3.3/library/subprocess.html?highlight=subprocess#subprocess.Popen.communicate
      process.kill()
      process.communicate()
      raise e

   exit_status = process.returncode
   return (exit_status, stdout, stderr)


def temp_file(data, suffix=''):
   handle, file_path = tempfile.mkstemp(suffix=suffix)
   f = os.fdopen(handle, 'w')
   f.write(data)
   f.close()
   return file_path



