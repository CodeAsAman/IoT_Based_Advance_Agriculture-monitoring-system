# call sub modules 
from .LoRaReceiverModule import LoRaReciver
# load other modules
import os,sys 
from SX127x.LoRa import MODE
from SX127x.board_config import BOARD 

# setup pin configuration 
#BOARD.setup()

# version 
__version__='0.1.0-stable'

# directory
__file__=os.getcwd()+'aiotReceiver/__init__.py'

# function to print version 
def version()->str:

    # print version
    print(__version__)
