x={'a':'aaa', 'b':'bbbb', 'c':12}
print(x['a'])
print(x['b'])
print(x['c'])

for key in x:
	print("key is %s, value is %s" %(key, x[key]))