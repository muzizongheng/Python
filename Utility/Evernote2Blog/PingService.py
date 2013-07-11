#Use this utility to get your all blogs from your provider, and ping them to search engine.

import AccessBlog
import AccessEN


#init evernote
evernote = AccessEN.Evernote()

#init config  & ping service urls
evernote.initConfig()
evernote.initPingServiceUrls()

#init blog provider
metaweblog = evernote.initBlog()

print(metaweblog.list_methods())


allBlogs = metaweblog.get_recent_posts(200)

for b in allBlogs:
	print(b['permalink'])
	evernote.pingBlog(b['permalink'])