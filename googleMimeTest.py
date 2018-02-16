#Google mimeTypes and mimeTypes are two different things!
#Do I created a conversion class
#It absolutely doesn't cover all cases
#
# All google mime types:
# application/vnd.google-apps.audio
# application/vnd.google-apps.document 	    Google Docs
# application/vnd.google-apps.drawing 	    Google Drawing
# application/vnd.google-apps.file 	    Google Drive file
# application/vnd.google-apps.folder 	    Google Drive folder
# application/vnd.google-apps.form 	    Google Forms
# application/vnd.google-apps.fusiontable   Google Fusion Tables
# application/vnd.google-apps.map 	    Google My Maps
# application/vnd.google-apps.photo
# application/vnd.google-apps.presentation  Google Slides
# application/vnd.google-apps.script 	    Google Apps Scripts
# application/vnd.google-apps.site 	    Google Sites
# application/vnd.google-apps.spreadsheet   Google Sheets
# application/vnd.google-apps.unknown
# application/vnd.google-apps.video
# application/vnd.google-apps.drive-sdk

__mts = {'application/vnd.google-apps.document': ('.docx', '.pdf'),
        'application/vnd.google-apps.presentation': ('.pptx', '.pdf'),
        'application/vnd.google-apps.spreadsheet': ('.xlsx', '.csv',  '.pdf')}
def googleMTtoExtension(googlemt, preferredExtension=None):
    if(not (googlemt in __mts)):
        raise ValueError('Submitted Google mime type is not a supported mime type!')

    if(preferredExtension is not None):
        if(preferredExtension in __mts[googlemt]):
            return preferredExtension
        raise ValueError('Submitted preferredExtension is not a valid extension of Google mime type: {0}!'.format(googlemt))
    else:
        return __mts[googlemt][0]

def extensionToGoogleMT(extension):
    googlemt = ''
    for mt in __mts:
        if(extension in __mts[mt]):
            return mt
    return ''
