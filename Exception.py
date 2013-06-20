s = "3q"

if s == "":
	raise Exception("Must not be empty")

try:
	i = int(s)
except Exception as err:
	print(err)
finally:
	print("good bye")