import tty, sys, termios

class bColors():

  colors = {
    "NOTICE" : '\033[95m', # Pink
    "INFO" : '\033[94m', # Blue
    "SUCCESS" : '\033[92m', # Green
    "WARNING" : '\033[93m', # Yellowish
    "FAIL" : '\033[91m', # Red
    "ENDC" : '\033[0m',
  }

class ReadChar():

  def __enter__(self):
      self.fd = sys.stdin.fileno()
      self.old_settings = termios.tcgetattr(self.fd)
      tty.setraw(sys.stdin.fileno())
      return sys.stdin.read(1)
  def __exit__(self, type, value, traceback):
      termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

class Debug():

  @staticmethod
  def println(level, message):
    print("  # " + bColors.colors[level] + level + bColors.colors["ENDC"] + " : " + message )
