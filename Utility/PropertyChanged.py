#Use this tool to Add private field and OnPropertyChanged function to C# property.

import re

class AutoGeneratorPropertyChangedTool:
	def __init__(self, filePath, baseClassName):
		#self.file = null
		self.filePath = filePath
		self.baseClassName = baseClassName

		self.classPattern = "(\s*public\s+%(class)s\s+%(derived)s\s+%(colon)s+\s*%(base)s)"%{'class':"class", 'derived':"\w+", 'colon':":", 'base':self.baseClassName}
		print(self.classPattern)

		self.propertyPattern = "(\s*public\s+%(type)s\s+%(property)s\s+%(getset)s)"%{'type':"\w+", 'property':"\w+", 'getset':"\{\s*get;\s*set;\s*\}"}
		print(self.propertyPattern)

	def isClass(self, data):
		result = re.match(self.classPattern, data)
		
		if result is None:
			return False
		else:
			return True

	def isProperty(self, data):
		result = re.match(self.propertyPattern, data)

		if result is None:
			return False
		else:
			return True

	def addField(property):
		return property

	def addPropertyChanged(property):
		return property 

print("Please input your inherited from class name: ")
baseClassName = input()
#baseClassName = "INotifyPropertyChanged"

print("Please input your c# class file path: ")
filePath = input()
#filePath = "D:/testProperty.txt"

tool = AutoGeneratorPropertyChangedTool(filePath, baseClassName)

file = open(filePath, "r")

for line in file:
	print("Line is: %s"%line)

	result = tool.isClass(line)
	print("Is class type: %s\n"%result)

	result = tool.isProperty(line)
	print("Is property type: %s\n"%result)