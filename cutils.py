# Library that takes all commands from custom psutil, custom subprocess and custom shutil and allows for execution of all of their function
from cpsutil import *
from csubprocess import *
from cshutil import *
from ccrypt import *
# This way, when importing cutil we can run cutil.popen (function popen from csubprocess) as well as cutil.copy (function copy from cshutil)

# Special functions
