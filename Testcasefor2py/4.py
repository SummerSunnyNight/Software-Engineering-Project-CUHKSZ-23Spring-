y = 1
def g():
    x = x + y
g()
x = 2 + y
def g(x=5):
    y = x + 1
g()



#enter line 2, local defined is y
#line 3, use=1

#enter line 6, local=x,y

#total use =1

#关于这里，我在网上查到的资料是函数重定义的话只会调用之前第一个method，请问是这样嘛？

#第四行，向上找到第一个函数，维护undefined_g：None
#第三行，undefined_g:x,use=1
#第八行，向上找到第一个函数，维护undefined_g:None

#总的use=1
