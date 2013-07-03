
#self is like "this" in c++
class Base:
	def __init__(self):
		self.data = []
	def add(self, x):
		self.data.append(x)

	def addtwice(self, x):
		self.add(x)
		self.add(x)

obase = Base()
obase.add("str1")
print(obase.data)
