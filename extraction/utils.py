import subprocess
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
   def alarm_handler(signum, frame):
      raise TimeoutError

   if timeout:
      signal.signal(signal.SIGALRM, alarm_handler)
      signal.alarm(timeout)
   try:
      (stdout, stderr) =  process.communicate(input_data)
      signal.alarm(0)
   except TimeoutError:
      process.kill()
      raise TimeoutError

   exit_status = process.returncode
   return (exit_status, stdout, stderr)

class TimeoutError(StandardError):
   pass
