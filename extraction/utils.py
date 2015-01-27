import subprocess32 as subprocess
import threading
import signal

def external_process(input_data, process_args, timeout=None):
   '''
   Pipes input_data via stdin to the process specified by process_args and returns the results

   Arguments:
      input_data -- the data to send
      process_args -- passed directly to subprocess.Popen(), see there for more details

   Returns:
      (stdout, stderr) -- a tuple of strings containing stdout and stderr data

   Examples:
      >>> external_process("Some String\nWith Data", ['grep', 'Data'])
      ('With Data\n', '')
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

