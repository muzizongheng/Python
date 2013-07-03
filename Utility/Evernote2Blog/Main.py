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

    if notebook.name != evernote.syncNotebook:
        continue

    filter = NoteStore.NoteFilter()
    filter.notebookGuid = notebook.guid

    noteCount = noteStore.findNoteCounts(authToken, filter, False).notebookCounts[notebook.guid]
    print("Find note counts: %i of %s"%(noteCount, notebook.name))

    #set note offset to loop find
    nextOffset = 0

    while nextOffset <  noteCount:
	    noteList = noteStore.findNotes(authToken, filter, nextOffset, noteCount)
	    print("Get %i notes, currrent note offset: %i\n"%(len(noteList.notes), nextOffset))

	    #increase offset for next find
	    nextOffset += len(noteList.notes)

	    #create blog category by tags
	    if evernote.isCreateTags == True:			
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

	    #print noteList
	    for n in noteList.notes:
	        print(n.title)

	        if (n.title+'\n' in currentBlogs) | (n.title in currentBlogs):
	            continue

	        #get note raw content
	        content = noteStore.getNoteContent(authToken, n.guid)
	        print("get note(%s) content successfuly"%(n.title))

	        #apply tags to blog
	        tags = noteStore.getNoteTagNames(authToken, n.guid)
	        print("get note(%s) tags successfuly"%(n.title))

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
	        while True:
		        try:
		            metaweblog.new_post(post, True)

		            print("publish note(%s) to blog successfully"%(n.title))
		            break
		        except Exception as e:
		            print(e)

		            #reinit blog
		            metaweblog = evernote.initBlog()
		        finally:
		            pass

	        #write note to existed file, and do not sync it in next time
	        existedBlog.write(n.title+'\n')
	        existedBlog.flush()

	        time.sleep(1)

	        # #write note
	        # try:
	        #     f = open(n.guid+".html", "w+", encoding='utf-8-sig')
	        #     f.write(content)
	        #     f.close()
	        # except Exception as err:
	        #     print(err)

	        print()

	    print()

    else:
    	print("get total notes of (%s) finished."%(notebook.name))

  	
existedBlog.close()

print("publish notes to blog successfully")
