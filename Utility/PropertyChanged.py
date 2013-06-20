#Use this tool to Add private field and OnPropertyChanged function to C# property.
#Author: Li Jiangong
#Version: 0.1

import re
import shutil

class AutoGeneratorPropertyChangedTool:
	def __init__(self, filePath, baseClassName):
		self.filePath = filePath
		self.baseClassName = baseClassName

		self.methodName = "OnPropertyChanged"

		self.classPattern = "(\s*public\s+%(class)s\s+%(derived)s\s+%(colon)s+\s*%(base)s)"%{'class':"class", 'derived':"\w+", 'colon':":", 'base':self.baseClassName}
		print(self.classPattern)

		self.propertyPattern = "(\s*public\s+(?P<property_type>%(type)s)\s+(?P<property_name>%(property)s)\s+%(getset)s)"%{'type':"\w+", 'property':"\w+", 'getset':"\{\s*get;\s*set;\s*\}"}
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

	def addField(self, propertyVariable):
		return "private %(type)s _%(name)s;"%('type':propertyVariable['property_type'], 'name':propertyVariable['property_name'])

	def addMethod(self, propertyVariable):
		return propertyVariable['property_name']

	def addPropertyChanged(self, property):
		result = "";
		result += self.addField(self.getPropertyName(property))
		result += self.addMethod(self.getPropertyName(property))
		return result 

	def getPropertyVariable(self, property):
		if property == "":
			raise Exception("Property is empty")

		m = re.match(self.propertyPattern, property)
		if m is None:
			raise Exception("Property is invalid, value is: %s"%property)

		print(m.group('property_type'))
		print(m.group('property_name'))

		variable = {'property_type':m.group('property_type'), 'property_name':m.group('property_name')}
		retun variable

print("Please input your inherited from class name: ")
#baseClassName = input()
baseClassName = "INotifyPropertyChanged"

print("Please input your c# class file path: ")
#filePath = input()
filePath = "D:/testProperty.txt"

tool = AutoGeneratorPropertyChangedTool(filePath, baseClassName)

#create backup file
fileBackupPath = filePath + "_bakcup"
shutil.copy2(filePath, fileBackupPath)
print("Create backup file successfully")

fileBackup = open(fileBackupPath, "r+")
file = open(filePath, "w+")

for line in fileBackup:
	print("Line is: %s"%line)

	result = tool.isClass(line)
	print("Is class type: %s\n"%result)

	result = tool.isProperty(line)
	print("Is property type: %s\n"%result)

	if result:
		file.write(tool.addPropertyChanged(line))
	else:
		file.write(line)

file.close()
fileBackup.close()

print("addPropertyChanged finished")