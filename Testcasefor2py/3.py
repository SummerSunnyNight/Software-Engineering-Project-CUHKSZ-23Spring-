x = 2
x = y + 2
def foo(x):
    x = x + 1

def func(z, x, y=6):
    x = y + z
    foo(x)

func(x, 4, y=5)


#line2, use =1

#enter line6, the local defined is x,y (每次进入一个函数，把之前的全局和自己的local并起来)
#line 7 use+1

#enter line3, local defined is None
#line 4 use=use+1
#total 3



#下面这种情况是defined
# x = 1

# def foo():
    
#     x = x+1