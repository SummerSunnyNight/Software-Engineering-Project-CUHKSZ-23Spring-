x = 1
x = y + 2
def func1(y):
    z = y*(5-2)
func1(y)
x = 1
x = x + 1
def foo1(y=2):
    y = z + 2
foo1()

#line 2 use=1

#enter line3,local define=None
#Line 4 use =use+1

#enter line8, local define=x,y
#line 9 use=use+1
#total use=3
