spath = "D:/copy.bat"
f = open(spath, "w")
f.write("@rem first line\n")
f.writelines("Second line\n")
f.writelines("Third line")
f.close()

f = open(spath, "r")
for line in f:
	print(line)