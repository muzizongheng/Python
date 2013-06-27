#
# A simple Evernote API demo script that lists all notebooks in the user's
# account and creates a simple test note in the default notebook.
#
# Before running this sample, you must fill in your Evernote developer token.
#
# To run (Unix):
#   export PYTHONPATH=../lib; python EDAMTest.py
#


import sys
import hashlib
import binascii
import time
import re
import hashlib

if "..\\Evernote\\lib" not in sys.path:
	sys.path.append("..\\Evernote\\lib")


import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors

#add title tag to html
def addTitle2Content(html, title):
    declare = "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
    replace = declare+"<title>"+title+"</title>"

    print("replace with: ", replace)
    print("replace result: ", html.replace(declare, replace))
    return html.replace(declare, replace)

#add evernote's tags to html
def addTags2Content(html, tags):
    data = "<![CDATA["
    for t in tags:
        data += t
        data += ","
    data += "]]>"

    return html+data;

#convert en-media node to img node of html
def replaceEnMediaWithImg(html, fileName, fileType, hashCode):
    if html == "":
        return ""

    #en-media regex pattern
    enMediaPattern = "(.*)(?P<en_media><en-media[^>]*?hash=\"%(hash)s\".*?((/>)|(></en-media>)))(.*)"%{'hash':hashCode}

    print(enMediaPattern)

    proc = re.compile(enMediaPattern, re.DOTALL | re.MULTILINE)
    validData = proc.match(html)
        
    if validData is None:
        print("valid failed")
        return html

    #get right en-media by hashcode & pattern
    enmedia = validData.group('en_media')    
    print("find en-media: ", enmedia)


    #replace en-media to img
    result = enmedia.replace("en-media", "img")
    src = "src=\"%s\""%(fileName+"."+fileType)
    result = result.replace("<img", "<img "+src)  
    print("after replaced, result is: ", result)  

    return html.replace(enmedia, result)

#get media type from mime
def getMediaType(enMedia):
    if enMedia == "":
        return

    index = enMedia.find("/")+1
    print("image type: ", enMedia[index:])

    return enMedia[index:]


# Real applications authenticate with Evernote using OAuth, but for the
# purpose of exploring the API, you can get a developer token that allows
# you to access your own Evernote account. To get a developer token, visit 
# https://sandbox.evernote.com/api/DeveloperToken.action
authToken = r"S=s1:U=72ef:E=146cb9ed03e:C=13f73eda440:P=1cd:A=en-devtoken:V=2:H=f9b4ecc463afe3aaee431b49c630943f"#"your developer token"

if authToken == "your developer token":
    print("Please fill in your developer token")
    print("To get a developer token, visit https://sandbox.evernote.com/api/DeveloperToken.action")
    exit(1)

# Initial development is performed on our sandbox server. To use the production 
# service, change "sandbox.evernote.com" to "www.evernote.com" and replace your
# developer token above with a token from 
# https://www.evernote.com/api/DeveloperToken.action
evernoteHost = "sandbox.evernote.com"
userStoreUri = "https://" + evernoteHost + "/edam/user"

userStoreHttpClient = THttpClient.THttpClient(userStoreUri)
userStoreProtocol = TBinaryProtocol.TBinaryProtocol(userStoreHttpClient)
userStore = UserStore.Client(userStoreProtocol)

versionOK = userStore.checkVersion("Evernote EDAMTest (Python)",
                                   UserStoreConstants.EDAM_VERSION_MAJOR,
                                   UserStoreConstants.EDAM_VERSION_MINOR)
print("Is my Evernote API version up to date? ", str(versionOK))
print("")
if not versionOK:
    exit(1)

# Get the URL used to interact with the contents of the user's account
# When your application authenticates using OAuth, the NoteStore URL will
# be returned along with the auth token in the final OAuth request.
# In that case, you don't need to make this call.
noteStoreUrl = userStore.getNoteStoreUrl(authToken)

print(noteStoreUrl)

noteStoreHttpClient = THttpClient.THttpClient(noteStoreUrl)
noteStoreProtocol = TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
noteStore = NoteStore.Client(noteStoreProtocol)

# List all of the notebooks in the user's account        
notebooks = noteStore.listNotebooks(authToken)
print("Found ", len(notebooks), " notebooks:")
for notebook in notebooks:
    print("  * ", notebook.name)

    filter = NoteStore.NoteFilter()
    filter.notebookGuid = notebook.guid
    noteList = noteStore.findNotes(authToken, filter, 0, 50)

    #print noteList
    for n in noteList.notes:
        print(n.title)

        #get note raw content
        content = noteStore.getNoteContent(authToken, n.guid)

        #add title to content
        content = addTitle2Content(content, n.title)

        #add tags to content
        tags = noteStore.getNoteTagNames(authToken, n.guid)
        content = addTags2Content(content, tags)

        #get resource & write to local    
        try:
            for res in n.resources:
                print("guid is: " + res.guid)
                print("width is: ", res.width)
                print("height is: ", res.height)

                attachment = noteStore.getResource(authToken, res.guid, True, False, True, False)

                fileType = getMediaType(res.mime)
                attachmentFile = open(res.guid+"."+fileType, "wb")
                attachmentFile.write(attachment.data.body)
                attachmentFile.close()

                #calculate hashcode for media
                md5 = hashlib.md5()
                md5.update(attachment.data.body)
                hashcode = md5.hexdigest()
                print("hast code: ", hashcode)

                #replace en-media to img
                content = replaceEnMediaWithImg(content, res.guid, fileType, hashcode)
        except Exception as e:
            print(e)
        finally:
            pass

        #write note
        try:
            f = open(n.guid+".html", "w+", encoding='utf-8-sig')
            f.write(content)
            f.close()
        except Exception as err:
            print(err)

        print()

    print()