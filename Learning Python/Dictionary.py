x={'a':'aaa', 'b':'bbbb', 'c':12}
print(x['a'])
print(x['b'])
print(x['c'])
print(x)

c = []
c.append(x)

for cc in c:
	print(cc)
for key in x:
	print("key is %s, value is %s" %(key, x[key]))

#write dict to file
dict = {}
dict['Test1'] = "ceshi"
dict['test2'] = "cadfasd"

import json
file = open('testDict', "w+")
writer = json.JSONEncoder()
print(writer.encode(dict).strip("{}"))

file.close()

#read file to dict
input_text = open('testDict').read()
input_json = "{%(input_text)s}" % vars()
reader = json.JSONDecoder()
config = reader.decode(input_json)

print(config)