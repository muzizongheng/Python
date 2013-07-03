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
import shutil
import json
from datetime import datetime

if "..\\Evernote\\lib" not in sys.path:
	sys.path.append("..\\Evernote\\lib")

import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors


import AccessBlog 


class Evernote:    
    def __init__(self):
        self.authToken = ""
        self.noteStoreUrl = ""
        self.blogType = "cnblogs"
        self.username = ""
        self.password = ""
        self.existedBlog = None

    #add title tag to html
    def addTitle2Content(html, title):
        declare = "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
        replace = declare+"<title>"+title+"</title>"

        print("replace with: ", replace)
        print("replace result: ", html.replace(declare, replace))
        return html.replace(declare, replace)

    #add evernote's tags to html
    def addTags2Content(html, tags):
        if tags is None:
            return html;

        data = "<![CDATA["
        for t in tags:
            data += t
            data += ","
        data += "]]>"

        return html+data;

    #convert en-media node to img node of html
    def replaceEnMediaWithImg(html, fileSrc, hashCode):
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
        src = "src=\"%s\""%(fileSrc)
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

    #convert notebook's tags to blog's category
    def convertTags2Category(tags):
        result = []
        for t in tags:
            c = AccessBlog.WpCategory(t.name, 0)
            result.append(c)

        return result

    #init blog (include: blog api, username, password)
    def initBlog(self):    
        if self.blogType == "":
            self.blogType = input("Please choose your blog api type, must be one of 'sina' or 'cnblogs'")

        self.blogType = self.blogType.lower()

        if self.blogType == "sina":
            self.server = "http://upload.move.blog.sina.com.cn/blog_rebuild/blog/xmlrpc.php"#"http://muzizongheng.cnblogs.com/services/metablogapi.aspx"
        else:
            self.server = "http://muzizongheng.cnblogs.com/services/metablogapi.aspx"

        print("blog server: ", self.server)    

        if self.username == "":
            self.username = input("Please input your username: ")
        
        if self.password == "":
            self.password = input("Please input your password: ")

        self.metaweblog = AccessBlog.WordPress(self.server, self.username, self.password)#AccessBlog.MetaWeblog(server, username, password)
        print("Support method: ", self.metaweblog.list_methods())

        return self.metaweblog

    #init evernote client
    def initEvernote(self):
        # Real applications authenticate with Evernote using OAuth, but for the
        # purpose of exploring the API, you can get a developer token that allows
        # you to access your own Evernote account. To get a developer token, visit 
        # https://sandbox.evernote.com/api/DeveloperToken.action
        if self.authToken == "":
            self.authToken = input("Please input your dev token: ")

        if self.authToken == "":
            print("Please fill in your developer token")
            print("To get a developer token, visit https://sandbox.evernote.com/api/DeveloperToken.action")
            exit(1)

        # Initial development is performed on our sandbox server. To use the production 
        # service, change "sandbox.evernote.com" to "www.evernote.com" and replace your
        # developer token above with a token from 
        # https://www.evernote.com/api/DeveloperToken.action

        # evernoteHost = "sandbox.evernote.com"
        # userStoreUri = "https://" + evernoteHost + "/edam/user"

        # userStoreHttpClient = THttpClient.THttpClient(userStoreUri)

        # userStoreProtocol = TBinaryProtocol.TBinaryProtocol(userStoreHttpClient)
        # userStore = UserStore.Client(userStoreProtocol)

        # Get the URL used to interact with the contents of the user's account
        # When your application authenticates using OAuth, the NoteStore URL will
        # be returned along with the auth token in the final OAuth request.
        # In that case, you don't need to make this call.
        if self.noteStoreUrl == "":
            self.noteStoreUrl = input("Please input your noteStoreUrl")#userStore.getNoteStoreUrl(authToken)

        print(self.noteStoreUrl)

        noteStoreHttpClient = THttpClient.THttpClient(self.noteStoreUrl)
        noteStoreProtocol = TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
        noteStore = NoteStore.Client(noteStoreProtocol)

        return noteStore

    #init config 
    # "authToken":"your dev auth token",
    # "noteStoreUrl":"your store",
    # "blogType":"your blog api",
    # "username":"",
    # "password":"",
    def initConfig(self):
        #read config
        input_text = open('config').read()
        input_json = "{%(input_text)s}" % vars() 
        reader = json.JSONDecoder()
        config = reader.decode(input_json)

        self.authToken = config["authToken"]
        self.noteStoreUrl = config["noteStoreUrl"]
        self.blogType = config["blogType"]
        self.username = config["username"]
        self.password = config["password"]

    #init published notes from file
    def initExistedBlog(self):
        self.existedBlog = open("existedBlog", "r+")
        shutil.copyfile("existedBlog", "existedBlog.bak")

        self.existedBlog.seek(0)
        currentBlogs = self.existedBlog.readlines()

        return currentBlogs