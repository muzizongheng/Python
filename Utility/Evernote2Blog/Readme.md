#Purpose

I create Evernote2Blog utility to convert my evernote's notes to blog of metaweblog type.
This utility use evernote's dev token and noteStore url (these information you can get from evernote dev site.) to access your evernote account, and get your notebooks' notes. After got that data, use metaweblog api to publish new blog  according your blog configuration.


#Configuration
This utility use two config files.

"config" config your auth token, notestoreUrl, username, password, and so on. May be like this:
    "authToken":"your dev auth token",
    "noteStoreUrl":"your store",
    "blogType":"your blog api",
    "username":"",
    "password":"",

"existedBlog" config you do not want to synced notes' title. If you add notes' title to this file, those notes can not be published to blog. 
