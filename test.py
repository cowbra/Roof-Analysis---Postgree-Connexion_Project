[a,b,c] =[1,2,3]
print(a)
print(b)
print(c)

[a,b,c] = [x+y for x,y in zip([a,b,c],[10,20,30])]

print(a)
print(b)
print(c)