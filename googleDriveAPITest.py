from __future__ import print_function
import httplib2
import os
import io
import argparse
import mimetypes
import googleMimeTest as googleMT
import json
from apiclient.http import MediaIoBaseDownload, MediaFileUpload

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json

def initParser():
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument("-d","--download", metavar='FILENAME',type=str, nargs='*', help="Download files with names containing FILENAME")
    parser.add_argument("-u","--upload", metavar='FILENAME', type=str, nargs='*', help="Upload files named FILENAME")
    parser.add_argument("-l","--list", action='store_true', help="List all files")
    parser.add_argument("-i","--install", action='store_true', help="Install app on google drive")
    flags = parser.parse_args()
    return flags

class GoogleDrive:
    __filePath = ''
    SCOPES = ['https://www.googleapis.com/auth/drive']
    CLIENT_SECRET_FILE = 'client_secret.json' #secret file needed to authenticate app
    APPLICATION_NAME = 'Drive API Python Quickstart'

    def __init__(self, install):
        if(install):
            credentials = self.__getCredentials('https://www.googleapis.com/auth/drive.install')
        else:
            credentials = self.__getCredentials()

        http = credentials.authorize(httplib2.Http())
        self.__driveService = discovery.build('drive', 'v3', http=http)
        mimetypes.init()

    def download(self, fileName):
        items = self.__find(fileName)
        for item in items:
            fileId = item['id']
            try:
                extension = googleMT.googleMTtoExtension(item['mimeType'])
                name = item['name']
            except ValueError:
                name, extension = os.path.splitext(item['name'])
            name = name.replace('.', '') #REMOVES . FROM FILE NAMES, FOR TESTING AND ONLY FOR TESTING
            mimeType = mimetypes.guess_type(name + extension)[0]

            request = self.__driveService.files().export_media(fileId=fileId, mimeType=mimeType) #In case of google Docs/Spreadsheets etc they do not have a type, but you can specify a type to export a file to by yourself. More info here: https://developers.google.com/drive/v3/web/manage-downloads
            fh = io.BytesIO() 
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print ("Download %d%%." % int(status.progress() * 100))
            self.__save(fh.getvalue(), name, extension);

    def upload(self, name): #simple upload for now, resumable uploads seem like a good option, but if processed files will be small, then it should be enough
        mimetype = mimetypes.guess_type(name)
        x, extension = os.path.splitext(name)
        file_metadata = {'name': name, 'mimeType': googleMT.extensionToGoogleMT(extension)} #mimetypes here are different than those in MediaFileUpload, they need to be set to use Google Docs/Spreadsheet etc 
        media = MediaFileUpload('{1}{0}'.format(self.__filePath, name), mimetype=mimetype[0])
        file = self.__driveService.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print ('File {0} has been uploaded'.format(name))

    def list(self):
        items = self.__find('')
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print('{0} ({1})'.format(item['name'], item['mimeType']))

    def __find(self, containsName):
        results = self.__driveService.files().list(q = "name contains '{0}'".format(containsName), fields="nextPageToken, files(id, name, mimeType)").execute() #Things which can be retrieved from files(): https://developers.google.com/drive/v3/reference/files#resource
        return results.get('files', [])

    def __save(self, fileBytes, fileName, extension):
        #Info on mimeTypes fo future: https://developers.google.com/drive/v3/web/mime-types
        with open('{0}{1}{2}'.format(self.__filePath, fileName, extension), 'wb') as out: 
            out.write(fileBytes)


    def __getCredentials(self, additionalScope=None):
        """Gets valid user credentials from storage.
    
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
    
        Returns:
            Credentials, the obtained credential.
        """
        if(additionalScope is not None and additionalScope not in self.SCOPES):
            self.SCOPES.append(additionalScope)
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                    'drive-python-quickstart.json')
    
        store = Storage(credential_path)
        credentials = store.get()

        getType = lambda https: [item.split('/')[-1] for item in https]

        credentialsTypes = []
        if(credentials is not None):
            credentialsTypes = getType(json.loads(credentials.to_json())['scopes'])

        scopesTypes = getType(self.SCOPES)

        credentialsNotSet = set(scopesTypes) - set(credentialsTypes)
        if not credentials or credentials.invalid or credentialsNotSet:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            flags = tools.argparser.parse_args(args=[]) #dummy flags needed
            credentials = tools.run_flow(flow, store, flags)
            print('Storing credentials to ' + credential_path)
        return credentials


    
def main():

    flags = initParser()
    if(flags.install):
        googleDrive = GoogleDrive(install=True)
    else:
        googleDrive = GoogleDrive(install=False)
    if(flags.download is not None):
        for fileName in flags.download:
            googleDrive.download(fileName)
    if(flags.upload is not None):
        for fileName in flags.upload:
            googleDrive.upload(fileName)
    if(flags.list):
        googleDrive.list()
    
if __name__ == '__main__':
    main()
