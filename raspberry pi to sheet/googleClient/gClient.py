# Source: https://developers.google.com/sheets/api/quickstart/python

# load os and json 
import os, json
# load warnings
import warnings 
# load google modules 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account 
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build,Resource
from googleapiclient.errors import HttpError

# make google client object 
class gClient(object):

    # define constructor 
    def __init__(self,token_path:str='token.json',SCOPES:list=None,
                 service_config:str='predefine-locals',
                 token_backup_path:str='credentials.json')->object:
        ''' make client object at gClient.client
            token_path : str :: path to google token for authorization credentials for
                                a desktop application
            SCOPES : list :: list of scopes
            sheet_config_file : str :: configuration dictionary path or predefine-locals.
                                       dictionary contains sheets (service) and its version
                                       as/like {'type':'sheets','version':'v4'}              
            token_backup_path : str :: path for backup file if token failed or not found
'''
        # credentials
        self.credentials=None
        # token file path
        self.token_path=token_path
        # backup file path
        self.token_backup_path=token_backup_path
        # scpoes - If modifying these scopes, delete the file token.json.
        if SCOPES==None:
            self.SCOPES=['https://www.googleapis.com/auth/spreadsheets.readonly','https://www.googleapis.com/auth/drive',
            		  'https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/spreadsheets']
        else:
            self.SCOPES=SCOPES
        # set service configuration
        if service_config=='predefine-locals':
            self.type='sheets'
            self.version='v4'
        # if service configuration given by user
        else:
            self.type=service_config['type']
            self.version=service_config['version']
        # ----------------------------------------------------------------------------------------
        # call function to make credentials
        self.__make_credentials()
        # call function to read config file
        self.client=build(self.type,self.version,credentials=self.credentials)


    # function to create
    def __make_credentials(self)->None:
        ''' to make credentials
'''
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        # check if file path exist 
        if os.path.exists(self.token_path):
            # read credentials
            try:
                self.credentials=Credentials.from_authorized_user_file(self.token_path,self.SCOPES)
                # make warn 
                warnings.warn('Credentials type - OAuth client! ............')
                # define credentials type
                credentials_type='OAuth client'
            # except as service client
            except ValueError:
                self.credentials=service_account.Credentials.from_service_account_file(self.token_path,scopes=self.SCOPES)
                # make warn 
                warnings.warn('Credentials type - Service account! ............')
                # define credentials type
                credentials_type='Service account'
        # If there are no (valid) credentials available, let the user log in.
        if (not self.credentials or not self.credentials.valid) and (credentials_type=='OAuth client'):
            # make user warn
            warnings.warn('Credentials invalid / not found .... Trying to update or solve issue ....')
            # if credentials has expired 
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                # make warn 
                warnings.warn('Credentials expired ! Updating ! ............')
                # make update credentials
                self.credentials.refresh(Request())
            # else if there are no credentials
            else :
                # make warn 
                warnings.warn(f'Credentials failed! using back up file at {self.token_backup_path} .....')
                # try to solve 
                flow=InstalledAppFlow.from_client_secrets_file(self.token_backup_path,self.SCOPES)
                # get credentials
                self.credentials=flow.run_local_server(port=0)
            # Save the credentials for the next run
            warnings.warn(f'Updating / Saving the credentials for the next run at {self.token_path}')
            # make save new / updated credentials
            try:
                # try to make save at path given for token 
                with open(self.token_path,'w+') as token:
                    token.write(creds.to_json())
            except FileNotFoundError:
                # if it failed to save at defined path 
                warnings.warn('FileNotFoundError! saving in bin/locally at "token.json"')
                # save in bin / locally in current working directory 
                with open(self.token_path,'w+') as token:
                    token.write(creds.to_json())
            

        # function to get service configuration
        def getClient(self)->Resource:
            ''' return google client
'''
            return self.client


# google sheet info class (use to convert from dictionary or
# from file to class object
class gSheetInfoClass(object):

    #  define constructor 
    def __init__(self,getInfoFrom,keys:set={'spreadsheetId','pattern','updatedRange',
                                            'updatedRows','updatedColumns','updatedCells'})->object:
        ''' used assign initinal values to google sheet info like sheet address, name,
            column from where to start etc.
            getInfoFrom : dictionary | string : dict containing key as attributes and
                          value as there value or, if string then the address of
                          binary file of dictionary object as string.
            keys : set : contains all the keys / attributes should be present              
'''
        # set attribute for required keys
        self.keys=keys       
        # try to set attributes 
        if isinstance(getInfoFrom,dict):
            # make store whole dictionary 
            self.gSheetInfoDict=getInfoFrom .copy()
            # call function to set attributes from dictionary
            self.__set_attributes_from_dictionary(self.gSheetInfoDict['current'].copy())
        # if it is not dictionary, i.e file address
        elif isinstance(getInfoFrom,str):
            if os.path.isfile(getInfoFrom):
                # make load and read
                with open(getInfoFrom,'r+') as gSheetInfoFile:
                    # make read using json
                    getInfoFrom=json.load(gSheetInfoFile)
                    # make store whole dictionary 
                    self.gSheetInfoDict=getInfoFrom 
                    # make call function to set attributes from dictionary
                    self.__set_attributes_from_dictionary(self.gSheetInfoDict['current'].copy())
            # else if file not found
            else:
                # raise error
                raise FileExistsError(f'No file at - {getInfoFrom}')
        # else if it is not a dictionay or string as file address
        else:
            #  raise error
            raise ValueError(f'getInfoFrom should be dictionary or string where the address of binary file of dictionary object as string')


    # define function to set attributes from dictionary
    def __set_attributes_from_dictionary(self,dictionary:dict)->None:
        ''' function to set attributes from dictionary
'''
        # check dictionary should contain all keys listed 
        if dictionary.keys()==self.keys:
            # set attributes
            for key,value in dictionary.items():
                # make done
                setattr(self,key,value)
        # else dictionary is empty
        else:
            # raise error
            raise ValueError(f'Dictionary recived do not contain all keys required! - key need {self.keys} but key found => {dictionary.keys()}')


    # function to update attributes from dictionary
    def updateAttributes(self,dictionary:dict)->None:
        ''' function to update gSheetInfoClass object's attributes by
            dictionary
'''
        # set attributes
        for key,value in dictionary.items():
            # make done
            setattr(self,key,value)


    # save all attributes current values
    def makeSave(self,saveAs='file',name='googleClient/gSheet.config'):
        ''' to save all attributes as dictionary or binary file
            saveAs : file | dictionary
            name : file name
'''
        # update current state
        self.gSheetInfoDict['current']=self.__dict__.copy()
        # make delete copy of dictionary itself (as it is also this class
        # attribute)
        del self.gSheetInfoDict['current']['gSheetInfoDict']
        # delete unwanted keys value
        del self.gSheetInfoDict['current']['keys']
        # make save as file
        if saveAs=='file':
            # make write
            try:
                with open(name,'w+') as gSheetFile:
                    # make dump
                    json.dump(self.gSheetInfoDict,gSheetFile)
                    # make return none
                    return None
            # if any error then return as dictionary
            except Exception as e:
                # make warn
                warnings.warn(f'Got error while saving file! Error:{e}')
                # make return dictionary
                return self.gSheetInfoDict
                
        # or
        else:
            # make return dictionary
            return self.gSheetInfoDict
