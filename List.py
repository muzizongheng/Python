word = ['a', 'b', 'c']

#index 0
a = word[0]
print(a)

#start index is 0, limit index is 2 and exclude 2
b = word[0:2]
print(b)

#start index is 0, and no limit index
c = word[0:]
print(c)

#limit index is 3, and exclude 3
d = word[:3]
print(d)

e = word[:2] + word[1:2]
print(e)

#last char
f = word[-1]
print(f)

del word[0]
print(word)