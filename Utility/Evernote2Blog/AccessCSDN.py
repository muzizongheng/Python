#Use this utility to access CSDN blog.
#Author: jiangong li
#Email: Jgli_2008@sina.com

import base64
from http import cookiejar
import urllib.request, urllib.parse, urllib.error

#url for accessing
csdnLoginUrl = r"http://passport.csdn.net/ajax/accounthandler.ashx?"
moduleUrl = r"http://write.blog.csdn.net/postedit/"
csdnAccessModuleUrl = r"http://passport.csdn.net/account/loginbox?callback=logined&hidethird=1&from="+urllib.parse.quote(moduleUrl)#http%3a%2f%2fwrite.blog.csdn.net%2f"

#install cookie
cj = cookiejar.CookieJar();
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj));
urllib.request.install_opener(opener)

#build request for accessed url
homeReq = urllib.request.Request(
	url = csdnAccessModuleUrl
	)

homeReq.add_header('Accept', 'text/html, application/xhtml+xml, */*');
homeReq.add_header('Accept-Language', 'en-US')
homeReq.add_header('Accept-Encoding', 'gzip, deflate')
homeReq.add_header('Connection', 'Keep-Alive');
homeReq.add_header('Referer', 'http://passport.csdn.net/account/login?from='+urllib.parse.quote(moduleUrl))#http%3a%2f%2fwrite.blog.csdn.net%2f')
homeReq.add_header('User-Agent', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)');

#open access url
resp = urllib.request.urlopen(homeReq)
print(resp.info())
print(resp.status)
print(cj)

################################################################################

#build request for login url
#post data
postdata = {
    'u':'muzizongheng',
    'p':'abc.123',
    'remember':'1',
    't':'log',
    'f':urllib.parse.quote(moduleUrl),
    }

postdata = urllib.parse.urlencode(postdata).encode('utf-8')
print(postdata)

req = urllib.request.Request(
	url = csdnLoginUrl,
	data = postdata)

req.add_header('Accept', 'text/html, application/xhtml+xml, */*');
req.add_header('Accept-Language', 'en-US')
req.add_header('Accept-Encoding', 'gzip, deflate')
req.add_header('Connection', 'Keep-Alive');
req.add_header('Referer', csdnAccessModuleUrl)
req.add_header('User-Agent', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)');

#open login url
r = urllib.request.urlopen(req)

print(r.status)
print(r.reason)
print(r.geturl())
print(r.info())

data = r.read().decode('utf-8')
print(data)
print(cj)