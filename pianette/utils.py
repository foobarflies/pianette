import tty, sys, termios

class bColors():

  colors = {
    "DEBUG" : '\033[30m', # GRAY
    "NOTICE" : '\033[95m', # Pink
    "INFO" : '\033[94m', # Blue
    "SUCCESS" : '\033[92m', # Green
    "WARNING" : '\033[93m', # Yellowish
    "FAIL" : '\033[91m', # Red
    "ENDC" : '\033[0m',
  }

class Debug():

  @staticmethod
  def println(level, message):
    print("  # " + bColors.colors[level] + level + bColors.colors["ENDC"] + " : " + message )
