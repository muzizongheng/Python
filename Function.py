def sum(a,b):
	return a+b

func = sum
r = func(5, 6)
print(r)


#provider default value
def add(a,b=2):
	return a+b

r = add(1)
print(r)

print(add(1, 5))

a = range(1, 10)
for x in a:
	print(x)

#the third parameter is step
a = range(-2, -11, -3)
for x in a:
	print(x)