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
def initBlog():        
    blogType = input("Please choose your blog api type, must be one of 'sina' or 'cnblogs'")
    blogType = blogType.lower()

    if blogType == "sina":
        server = "http://upload.move.blog.sina.com.cn/blog_rebuild/blog/xmlrpc.php"#"http://muzizongheng.cnblogs.com/services/metablogapi.aspx"
    else:
        server = "http://muzizongheng.cnblogs.com/services/metablogapi.aspx"

    print("blog server: ", server)    

    username = ""
    password = ""

    username = input("Please input your username: ")
    password = input("Please input your password: ")

    metaweblog = AccessBlog.WordPress(server, username, password)#AccessBlog.MetaWeblog(server, username, password)
    print("Support method: ", metaweblog.list_methods())

    return metaweblog

# #init evernote client
# def initEvernote():
#     consumerKey = "muzizongheng-8753"
#     consumerSecret = "a25670f5b2fe425e"
#     tokenKey = ""
#     tokenSecret = ""
#     apiUrl = "sandbox.evernote.com"

#     consumer = oauth.Consumer(key = consumerKey, secret = consumerSecret)
#     token = oauth.Token(key = tokenKey, secret = tokenSecret)

#     params['oauth_token'] = token.key
#     params['oauth_consumer_key'] = consumer.key
#     client = oauth.Client(consumer)
#     request_token_content = client.request("https://"+apiUrl+"/oauth", "POST")
#     request_token = request_token["oauth_token"]
#     tokenurl = "https://"+apiUrl+"/OAuth.action?oauth_token=" + request_token

#     print(tokenurl)

#     return tokenurl

# Real applications authenticate with Evernote using OAuth, but for the
# purpose of exploring the API, you can get a developer token that allows
# you to access your own Evernote account. To get a developer token, visit 
# https://sandbox.evernote.com/api/DeveloperToken.action
authToken = "your developer token"

if authToken == "your developer token":
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

# versionOK = userStore.checkVersion("Evernote EDAMTest (Python)",
#                                    UserStoreConstants.EDAM_VERSION_MAJOR,
#                                    UserStoreConstants.EDAM_VERSION_MINOR)
# print("Is my Evernote API version up to date? ", str(versionOK))
# print("")
# if not versionOK:
#     exit(1)

# Get the URL used to interact with the contents of the user's account
# When your application authenticates using OAuth, the NoteStore URL will
# be returned along with the auth token in the final OAuth request.
# In that case, you don't need to make this call.
noteStoreUrl = "https://www.evernote.com/shard/s54/notestore"#userStore.getNoteStoreUrl(authToken)

print(noteStoreUrl)

noteStoreHttpClient = THttpClient.THttpClient(noteStoreUrl)
noteStoreProtocol = TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
noteStore = NoteStore.Client(noteStoreProtocol)

#init blog
metaweblog = initBlog()

currentBlogs = ['TTS API 使用', '获取.net对象的属性集', 'C# Json库 和 xml 序列化反序列化 存在的问题', 'WPF DatePicker 的textbox的焦点', 'WPF 使用MultiBinding ，TwoWay ，ValidationRule ，需要注意的事项', 
    'WPF TreeView 后台C#选中指定的Item， 需要遍历', 'WPF GridViewColumn Sort DataTemplate', 'WPF Get Multibinding Expression， Update Source，', 'WPF 后台触发 Validate UI‘s Element', 'WPF ValidationRule 触发ErrorTemplate 的注意事项', 
    'C# 线程的暂停和恢复的 实现', 'WPF DelegateCommand CanExecute', 'WaitHandle.WaitAll 方法在WPF工程中的应用', 'C#支持从自定义日期时间格式到DateTime类型', 'kindle3 破解字体', 'WPF ListView VisualPanel',
    '如何在kindle 3上无法进入 http://www.google.com/reader, 先登陆www.google.com， 然后选择阅读器。' ]

# List all of the notebooks in the user's account        
notebooks = noteStore.listNotebooks(authToken)
print("Found ", len(notebooks), " notebooks:")
for notebook in notebooks:
    print("  * ", notebook.name)

    if notebook.name != "自我心的":
        continue


    filter = NoteStore.NoteFilter()
    filter.notebookGuid = notebook.guid
    noteList = noteStore.findNotes(authToken, filter, 0, 50)

    create blog category by tags
    tagslist = noteStore.listTagsByNotebook(authToken, notebook.guid)
    categories = convertTags2Category(tagslist)
    try:
        for c in categories:
            metaweblog.new_category(c)
            print("create blog's category: ", c.name)
    except Exception as err:
        print("Create category failed: ", err)
    finally:
        pass

    i = 0

    #print noteList
    for n in noteList.notes:
        print(n.title)

        if n.title in currentBlogs:
            continue

        #set note's tilte to blog id, and use blog id to host note's resource
        blogId = n.title

        #get note raw content
        content = noteStore.getNoteContent(authToken, n.guid)

        #add title to content
        #content = addTitle2Content(content, n.title)

        #apply tags to blog
        tags = noteStore.getNoteTagNames(authToken, n.guid)

        #get resource & write to local    
        try:
            if n.resources is not None:
                for res in n.resources:
                    print("guid is: " + res.guid)
                    print("width is: ", res.width)
                    print("height is: ", res.height)
                    print("resource type is: ", res.mime)

                    attachment = noteStore.getResource(authToken, res.guid, True, False, True, False)

                    #fileType = getMediaType(res.mime)
                    # attachmentFile = open(res.guid+"."+fileType, "wb")
                    # attachmentFile.write(attachment.data.body)
                    # attachmentFile.close()

                    #upload resource to blog
                    fileData = AccessBlog.FileData(attachment.data.body, res.guid, res.mime)
                    fileUrl = metaweblog.new_media_object(fileData)

                    #calculate hashcode for media
                    md5 = hashlib.md5()
                    md5.update(attachment.data.body)
                    hashcode = md5.hexdigest()
                    print("hast code: ", hashcode)

                    #replace en-media to img
                    content = replaceEnMediaWithImg(content, fileUrl.url, hashcode)
        except Exception as e:
            print(e)
        finally:
            pass

        #publish note to blog
        post = AccessBlog.Post(datetime.now(), content, n.title, tags)
        metaweblog.new_post(post, True)

        i++

        if i >= 12:
            #reinit blog
            metaweblog = initBlog()
            continue

        time.sleep(60)

        # #write note
        # try:
        #     f = open(n.guid+".html", "w+", encoding='utf-8-sig')
        #     f.write(content)
        #     f.close()
        # except Exception as err:
        #     print(err)

        print()

    print()

print("publish notes to blog successfully")