# load aiot-receiver-module
import aiotReceiver as iotr
# google client module
from googleClient.gClient import gClient,gSheetInfoClass
# load re module for string purification
import re
# load datetime module
import datetime
# load pandas for dataframe
import pandas as pd
# load input output module
import io
# load module to save and read object
import pickle
# load module read json file (config file)
import json
# some backend modules
from googleapiclient.discovery import Resource as gClientSheetObject

# Note: pandas version less than 1.0.x may lead to errors

#######################################################################################################################

# define variables for module

# load LoRa Reciver config file
with open('LoRaReceiver.config','rb+') as LoRaReceiverConfigFile:
    # make assign to python object, i.e dictionary
    LoRaReceiverConfig=pickle.load(LoRaReceiverConfigFile)

# define allowed characters (vaild characters comming from IoT nodes)
allowedChar=LoRaReceiverConfig['current']['allowedChar']['value']
# define character with which we have to fill non-valid characters
filledWith=LoRaReceiverConfig['current']['filledWith']['value']
# sensor names / symbols connected to IoT nodes 
sensorsNames=LoRaReceiverConfig['current']['sensorsNames']['value']
# make column order (save in same oder in google sheets)
columnOrder=LoRaReceiverConfig['current']['columnOrder']['value']
# make update to google sheet after 10 minutes (default)
makeUpdateAfterMinutes=LoRaReceiverConfig['current']['makeUpdateAfterMinutes']['value']
# the method use to upload data values to google sheets
# for more info look here: https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption
valueInputOption=LoRaReceiverConfig['current']['valueInputOption']['value']
# make dataframe to store temporary data between two significant updates
dataframe=pd.DataFrame(columns=columnOrder) # empty dataframe

# get google client info (need key like here - aiot-data-handler-key.json)
# to make a key see - https://developers.google.com/sheets/api/quickstart/python
client=gClient('aiot-data-handler-key.json')

# make sheet info dictionary object by reading json file at - "googleClient/gSheet.config"
with open('googleClient/gSheet.config','r+') as aiotConfigFile:
    # make read json
    gSheetInfoDict=json.load(aiotConfigFile)
# convert dictionay to gSheetInfo (gSheetInfoClass object)
gSheetInfo=gSheetInfoClass(gSheetInfoDict)

# google sheet reading and writting object from google client
gClientSheetObjectVariable=client.client.spreadsheets()

########################################################################################################################################

# functions required

# define data cleaner function
def makeDataClean(payload:str,allowedChar:str=allowedChar,
                  filledWith:str=filledWith)->str:
    ''' function to clean data and remove unwanted characters
        allowed characters are a to z, A to Z, 1 to 9 and ;,:. 
'''
    # remove all unrequired characters
    return re.sub(allowedChar,filledWith,payload)


# function to convert data from raw value to dictionary
def rawData2Dict(rawData:str,sensorsNames:set=sensorsNames)->dict:
    ''' function to clean data (string) from raw data to proper dictionary format
'''
    # define processed dictionary (data)
    processedData=dict()
    # make data split by semi-colon  (';')
    rawData=rawData.split(';')
    # check is there complete data
    if len(rawData)>1:                  # i.e. ";" is there in string due to which
                                        # it should split atleast in two elements
        # make read each element in list
        for index,element in enumerate(rawData):
            # make split element
            element=element.split(':')
            # if it is not a null string 
            if not element:
                # if it for first element
                if index==0:
                    return False
                # else
                else:
                    continue
            # if it is first element of list
            if index==0:
                # first element contain node name and length should be
                # four like [NodeName,'','valueNames','values']
                if len(element)==4:
                    # get node name
                    # convert each value to single list item (can be easily converted to dataframe)
                    processedData['Node']=[re.sub(r'[^0-9]','',element[0])]
                    # number of sensors names should be equal to sensor values
                    #if len(element[2].split(','))==len(element[3].split(',')):
                    # get sensor name and values
                    for sName,sValue in zip(element[2].split(','),element[3].split(',')):
                        # check if sensor name is available
                        if sName in sensorsNames:
                            # try to add to dictionary
                            try:
                                # convert each value to float type
                                processedData[sName]=float(sValue)
                            except Exception:
                                continue
                        # make leave if sensor name is not there
                        else:
                            continue
                    # if values are not equal to sensor names
                    #else:
                        #continue
                # else leave out all and EXIT (Seneor name not found!)
                else:
                    return False
            # else for other than first value 
            else:
                # split (length should be two) as 'name:value'
                if len(element)==2:
                    # number of sensors names should be equal to sensor values
                    #if len(element[2].split(','))==len(element[3].split(',')):
                    # get sensor name and values
                    for sName,sValue in zip(element[0].split(','),element[1].split(',')):
                        # check if sensor name is available
                        if sName in sensorsNames:
                            # try to add to dictionary
                            try:
                                # convert each value to float type
                                processedData[sName]=float(sValue)
                            except Exception:
                                continue
                        # make leave if sensor name is not there
                        else:
                            continue
                    # if values are not equal to sensor names
                    #else:
                        #continue
                # else move to next
                else:
                    continue
    # make other sensor value (not present) to null
    for sName in sensorsNames:
        # check 
        if sName not in processedData:
            # make it None
            processedData[sName]=None
    # add date and time to dictionary column as string (as further it has to be converted to json
    # and datetime type is not convertible) 
    processedData['datetime']=datetime.datetime.now()
    # make return processed data dictionary
    return processedData    


# define function what to do on receive
def function_on_recive(payload:str)->None:
    ''' function called by lora to give data recived!
        call -> makeDataClean to clean raw values and remove unwanted values 
        call -> rawData2Dict to convert raw straing to dictionary 
        call -> handleProcessedValues 
'''
    # call function to clean data
    payload=makeDataClean(payload)
    # make recived data print
    print('Received:',payload)
    # convert from raw data to processed dictionary
    payload=rawData2Dict(payload)
    # handle data
    handleProcessedValues(payload)


# function to handle processed values as pandas dataframe
def handleProcessedValues(processedData:dict,sumed_after:int=makeUpdateAfterMinutes)->None:
    ''' processedData : dictionary of pocessed data
        sumed_after : number of minutes average value have to be calculated
        for more info look here: https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption
'''
    # get dataframe as global variable 
    global dataframe,gSheetInfo
    # convert "sumed_after" todatetime.timedelta
    sumed_after=datetime.timedelta(minutes=sumed_after)
    # try to add data (dictionary) to temporary pandas dataframe
    try :
        dataframe=pd.concat([dataframe,pd.DataFrame(processedData)])
    except ValueError:
        print(f'Value Error: got invalid value while updating dataframe -> {processedData}')
    # check shape (rows) of temporary dataframe (greater than one rows)
    if dataframe.shape[0]>1:
        # and if time delta (time difference) is greater than sumed_after (10 default) minutes
        if (dataframe.iloc[-1].datetime-dataframe.iloc[0].datetime) >= sumed_after:
            # make sum and calculate average value by node (group) and update sheet info 
            gSheetInfo=updateGSheet(dataframe.groupby(by='Node').mean().reset_index())
            # make dataframe empty
            dataframe.drop(dataframe.index,inplace=True)


# function to sent values to google sheet 
def updateGSheet(dataframe:pd.DataFrame,gClientSheetObject:gClientSheetObject=gClientSheetObjectVariable,
                 columnOrder:list=columnOrder,gSheetInfo:gSheetInfoClass=gSheetInfo,
                 valueInputOption=valueInputOption)->gSheetInfoClass:
    ''' function to update google sheet, i.e send values to google sheets
        dataframe : pandas.DataFrame : averaged value of each "Node"
        gClientSheetObject : google client sheet object used to upadate, read or write sheeet
        columnOrder : list : the order of column in which thet have to be filled in sheet
        valueInputOption : str : the method use to upload data values to google sheets
'''
    # make google info dictionary as global
    #global gSheetInfo
    # preprocessed data (convert all values to string (as they can be easly jsonify)
    dataframe=dataframe[columnOrder].astype(str)
    # make update value all
    gSheetInfo.updateAttributes(gClientSheetObject.values().update(spreadsheetId=gSheetInfo.spreadsheetId,
                                                                   range=gSheetInfo.pattern[:-3],
                                                                   valueInputOption=valueInputOption,
                                                                   body={'values':dataframe.values.tolist()}).execute())
    # make update pattern
    gSheetInfo.pattern=gSheetInfo.pattern[:-4]+str(gSheetInfo.updatedRows+1)+':??'
    # make return updated gSheetInfo
    return gSheetInfo

    
# function to add / update column names
def updateColumnNames(gClientSheetObject:gClientSheetObject,columnNames:list,gSheetInfo:gSheetInfoClass,
                      atRow:str=str(1),valueInputOption=valueInputOption)->gSheetInfoClass:
    ''' function to add column name to sheet at row 1 (default)
        gClientSheetObject : sheet object googleapiclient.discovery.Resource
        columnNames : list : names of column to be updated on gooogle sheets
        gSheetInfo : gSheetInfoClass : contains google sheet information
        atRow : int : at which row column names has to be upadated
        valueInputOption : str : input method to sheet 
'''
    # make update value all
    gSheetInfo.updateAttributes(gClientSheetObject.values().update(spreadsheetId=gSheetInfo.spreadsheetId,
                                                                   range=gSheetInfo.pattern[:-4]+atRow,
                                                                   valueInputOption=valueInputOption,
                                                                   body={'values':[columnNames]}).execute())
    # make update pattern
    gSheetInfo.pattern=gSheetInfo.pattern[:-4]+str(gSheetInfo.updatedRows+1)+':??'
    # make return updated gSheetInfo object (updated)
    return gSheetInfo

    
########################################################################################################################


# call main function
if __name__=='__main__':

    # setup pin configuration
    iotr.BOARD.setup()

    # make lora object
    loraRx=iotr.LoRaReciver(function_on_recive,wait_4=0.5,makePrint=True,
                            deep_verbose=False)
    # make LoRa in standby
    loraRx.set_mode(iotr.MODE.STDBY)
    # Range:  Defaults -> 434.0MHz, Bw=125kHz, Cr=4/5, Sf=128chips/symbol
    # CRC on 13dBm
    loraRx.set_pa_config(pa_select=1)
    # make start LoRa Loop 
    try:
        # update column names
        gSheetInfo=updateColumnNames(gClientSheetObjectVariable,columnNames=columnOrder,gSheetInfo=gSheetInfo,
                                     atRow=str(1),valueInputOption=valueInputOption)
        # make start LoRa infinite loop
        loraRx.startLoRa()
    # except keyboard interruption
    except KeyboardInterrupt:
        # make a note
        iotr.sys.stdout.write('Closing connection .............')
    # make close all finally
    finally:
        # make update sheet info dictionary object by reading json file at -
        # "googleClient/gSheet.config"
        gSheetInfo.makeSave()
        # all flush
        iotr.sys.stdout.flush()
        # make all set
        loraRx.set_mode(iotr.MODE.SLEEP)
        # make all connection done
        iotr.BOARD.teardown()
