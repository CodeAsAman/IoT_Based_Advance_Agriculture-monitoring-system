# load module 
from .gClient import gClient

# load os module 
import os 

# version 
__version__='0.1.0-stable'

# directory
__file__=os.getcwd()+'googleClient/__init__.py'

# function to print version 
def version()->str:

    # print version
    print(__version__)
