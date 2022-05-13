# load modules
import time,sys
from SX127x.LoRa import LoRa,MODE
from SX127x.board_config import BOARD 

# setup pin configuration 
BOARD.setup()

# define LoRa reciver class 
class LoRaReciver(LoRa):


    # define constructor 
    def __init__(self,function_on_recive,wait_4:float=0.5,makePrint:bool=True,
                 deep_verbose:bool=False)->object:
        """ class constructor
            function_on_recive : function in which recived payload is passed
            wait_4 : make wait program for before next reading
            makePrint : either to print each receiving
            deep_verbose : LoRa.verbose """ 
        # call parent constructor
        super(LoRaReciver,self).__init__(verbose=deep_verbose)
        # define intinal value of functions   
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])
        # set function to do on reciving values 
        self.function_on_recive=function_on_recive
        # make wait before each readings
        self.wait_4=wait_4
        # if detailed printing
        self.makePrint=makePrint
    
        
    # define starting function 
    def startLoRa(self)->None:
        """ function to start LoRa communication """
        # make reset RX channel 
        self.reset_ptr_rx()
        # change mode
        self.set_mode(MODE.RXCONT)
        # start reciving data
        while True:
            # make function wait (for 200 miliseconds) 
            time.sleep(self.wait_4)
            # make call for value
            _=self.get_rssi_value()
            # get status (update)
            _=self.get_modem_status()
            # make clean
            sys.stdout.flush()


    # define function that what to do on reciving value
    def on_rx_done(self)->None:
        # make read value
        self.clear_irq_flags(RxDone=1)
        # make read payload
        payload=self.read_payload(nocheck=True)
        # decode payload
        payload=bytes(payload).decode(encoding='UTF-8',errors='ignore')
        # make print if
        if self.makePrint:
            # make print
            print('\nReceived:',payload)
        # forward data to data handler function
        self.function_on_recive(payload)
        # make sleep
        self.set_mode(MODE.SLEEP)
        # make channel reset
        self.reset_ptr_rx()
        # change mode again
        self.set_mode(MODE.RXCONT)
