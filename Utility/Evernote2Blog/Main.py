#Use this tool to get notes from evernote, and publish these notes to blog
#Author: Li Jiangong
#Email: jgli_2008@sina.com

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

import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors


import AccessEN 
import AccessBlog

#start task to process evernote's notes to convert to blog
#init evernote
evernote = AccessEN.Evernote()

#init config & existed blog
evernote.initConfig()
currentBlogs = evernote.initExistedBlog()
existedBlog = evernote.existedBlog

noteStore = evernote.initEvernote()
authToken = evernote.authToken

#init blog
metaweblog = evernote.initBlog()

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

    #create blog category by tags
    # tagslist = noteStore.listTagsByNotebook(authToken, notebook.guid)
    # categories = convertTags2Category(tagslist)
    # try:
    #     for c in categories:
    #         metaweblog.new_category(c)
    #         print("create blog's category: ", c.name)
    # except Exception as err:
    #     print("Create category failed: ", err)
    # finally:
    #     pass

    #print noteList
    for n in noteList.notes:
        print(n.title)

        if (n.title+'\n' in currentBlogs) | (n.title in currentBlogs):
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

        try:
            #publish note to blog
            post = AccessBlog.Post(datetime.now(), content, n.title, tags)
            metaweblog.new_post(post, True)
        except Exception as e:
            print(e)

            #reinit blog
            self.metaweblog = AccessEN.initBlog()
            print("Support method: ", self.metaweblog.list_methods())
            metaweblog = self.metaweblog
        finally:
            pass

        #write note to existed file, and do not sync it in next time
        existedBlog.write(n.title+'\n')

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

existedBlog.close()

print("publish notes to blog successfully")