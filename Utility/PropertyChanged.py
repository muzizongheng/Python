#Use this tool to Add private field and OnPropertyChanged function to C# property.
#Author: Li Jiangong
#Email: jgli_2008@sina.com
#Version: 0.2
#coding=utf-8

import re
import shutil

class AutoGeneratorPropertyChangedTool:
	def __init__(self, filePath, baseClassName, propertyChangedName):
		self.filePath = filePath
		self.baseClassName = baseClassName

		self.methodName = propertyChangedName

		self.classPattern = "(\s*public\s+%(class)s\s+%(derived)s\s+%(colon)s+\s*%(base)s)"%{'class':"class", 'derived':"\w+", 'colon':":", 'base':self.baseClassName}
		print(self.classPattern)

		self.propertyPattern = "((?P<space>\s*)public\s+(?P<property_type>%(type)s)\s+(?P<property_name>%(property)s)\s*%(getset)s)"\
			%{'type':"\w+", 'property':"\w+", 'getset':"\{((\s*get;\s*set;\s*)|(\s*set;\s*get;\s*))\}"}
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
		return "%(space)sprivate %(type)s %(field)s;\n"%{'space':propertyVariable['space'], 'type':propertyVariable['property_type'], 'field':self.getFieldName(propertyVariable['property_name'])}

	def addMethod(self, propertyVariable):
		result = "%(space)spublic %(type)s %(name)s\n"%{'space':propertyVariable['space'], 'type':propertyVariable['property_type'], 'name':propertyVariable['property_name']}
		result += "%(space)s{\n"%{'space':propertyVariable['space']}
		result += "%(space)s\tget{return %(field)s;}\n"%{'space':propertyVariable['space'], 'field':self.getFieldName(propertyVariable['property_name'])}
		result += "%(space)s\tset\n%(space)s\t{\n%(space)s\t\t%(field)s = value;\n%(space)s\t\tOnPropertyChanged(\"%(name)s\");\n%(space)s\t}\n"\
			%{'space':propertyVariable['space'], 'field':self.getFieldName(propertyVariable['property_name']), 'name':propertyVariable['property_name']}
		result += "%(space)s}\n"%{'space':propertyVariable['space']}

		result += "\n"

		return result

	def addPropertyChanged(self, property):
		result = "";

		varialbe = self.getPropertyVariable(property)
		result += self.addField(varialbe)
		result += self.addMethod(varialbe)

		print(result)
		
		return result 

	def getPropertyVariable(self, property):
		if property == "":
			raise Exception("Property is empty")

		m = re.match(self.propertyPattern, property)
		if m is None:
			raise Exception("Property is invalid, value is: %s"%property)

		result = m.groupdict()

		return result

	def getFieldName(self, propertyName):
		result = propertyName
		firstChar = "_" + result[0].lower()
		result = result.replace(result[0], firstChar, 1)

		return result


# Currently no need to input base class name
# print("Please input your inherited from class name: ")
# baseClassName = input()
# if baseClassName == "":
# 	baseClassName = "INotifyPropertyChanged"

print("Please input your adding method name: ")
methodName = input()
if methodName == "":
	methodName = "OnPropertyChanged"


print("Please input your c# class file path: ")
filePath = input()
if filePath == "":
	filePath = "D:/testProperty.txt"

tool = AutoGeneratorPropertyChangedTool(filePath, "", methodName)

#create backup file
fileBackupPath = filePath + "_bakcup"
shutil.copy2(filePath, fileBackupPath)
print("Create backup file successfully")

fileBackup = open(fileBackupPath, "r+")
file = open(filePath, "w+")

for line in fileBackup:
	print("Line is: %s"%line)

	#Currently not need to judge class name
	#result = tool.isClass(line)
	#print("Is class type: %s\n"%result)

	result = tool.isProperty(line)
	print("Is property type: %s\n"%result)

	if result:
		file.write(tool.addPropertyChanged(line))
	else:
		file.write(line)

file.close()
fileBackup.close()

print("addPropertyChanged finished")