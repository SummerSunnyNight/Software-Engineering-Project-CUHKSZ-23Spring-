import ast

# source='''
# x = 1
# def foo2():
#     y = x + 1
# foo2()
# x = y + 2
# def func1(y):
#     z = y*(5-2)
# def foo(x=5, y=6):
#     func1(y)
# foo()
# def foo3(x=10):
#     x = y + 10
# foo()
# foo2()


# '''
source = input()
source = "\n".join(source.split("\\n"))




Overall_undefined_Use=0



#The Following are functions used to find the unused functions and delete them from the original code

def find_function_definitions(code_str):
    """
    Finds all function definitions in the given Python code string and returns them as a tuple of
    the function definition name, corresponding line number of the definition line, and the function
    definition node.
    """
    tree = ast.parse(code_str)
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append([node.name, node.lineno, node,0])#第四位作为有没有use的flag
    
    return functions

def find_function_calls(code_str):
   
    tree = ast.parse(code_str)
    function_calls = []
    
    for node in tree.body:
        if isinstance(node, ast.Expr):
            function_calls.append([node.value.func.id, node.lineno, node])
    
    return function_calls


class FunctionDeletionTransformer(ast.NodeTransformer):
    def __init__(self, lineno_list):
        self.lineno_list = lineno_list

    def visit_FunctionDef(self, node):
        if node.lineno in self.lineno_list:
            # Return None to delete the node
            return None
        else:
            # If the node is not in the list to delete, return it as is
            return node

def remove_unused_functions(code):
    function_def=find_function_definitions(code)
    function_calls=find_function_calls(code)
    

    def flag_the_used_function_def(function_call):#所有的使用过的function_def都会被标成1。没使用过的则是0
        #match the func call with the function definition
        nonlocal function_def
        match_func_definitions=[function for function in function_def if function[0]==function_call[0]]#先筛选出名字一样的#注意这里是浅拷贝
        if len(match_func_definitions)==0:
            #如果名字一样的都没有，那么就结束
            return
        else:
            Func_list_to_sort=[function for function in match_func_definitions if function[1]<function_call[1]]#只有def在call之前的才会被call
            #没有在func之前的也pass
            if len(Func_list_to_sort)==0:
                return
            else:
                #有名字一样的，找到line在之前第一个的（也就是sort找lino最大的）
                Func_list_to_sort.sort( key=lambda x: x[1], reverse=True)
                function_to_use=Func_list_to_sort[0]
                #找到了要用的function以后，把这个functiondef里的flag设置为1
                function_to_use[3]=1
                #进入function body，找到里面所有的function_call，然后重复这个函数
                inner_functionCalls=[]

                for node in function_to_use[2].body:
                    if isinstance(node, ast.Expr):
                        inner_functionCalls.append([node.value.func.id, node.lineno, node])
                if len(inner_functionCalls)==0:#如果长度是0，说明这个function内部没有再call function，return
                    return
                else:
                    #如果长度不是0，说明还有call
                    for inner_functionCall in inner_functionCalls:
                        flag_the_used_function_def(inner_functionCall)
                    
                

    for one_function_call in function_calls:
        flag_the_used_function_def(one_function_call)
    
    #delete the unused function according to the flag




    tree=ast.parse(code)
    nodes_to_remove=[]
    for function in function_def:
        if function[3]==0:#flag 0 means unused
            nodes_to_remove.append(function[1])#注意到这里两个object其实是没法互相指向的，还是得用lineno
    


    # Apply the transformer to the AST
    transformed_tree = FunctionDeletionTransformer(nodes_to_remove).visit(tree)


 
    return ast.unparse(transformed_tree)









# def find_function_definitions(code_str):
#     """
#     Finds all function definitions in the given Python code string and returns them as a tuple of
#     the function definition name, corresponding line number of the definition line, and the function
#     definition node.
#     """
#     tree = ast.parse(code_str)
#     functions = []
    
#     for node in ast.walk(tree):
#         if isinstance(node, ast.FunctionDef):
#             functions.append((node.name, node.lineno, node))
    
#     return functions
# print(find_function_definitions(source))


#备份一下这里，微信上的文件是直接运行py1和2的

#关于有函数的话思路是什么，我想的是这样的
#对第一层每个node除了func def以外按顺序run，run到全部结束为止，如果是正常的code你已经写好了。
# 是func的话首先是有一个transformer，决定func里的local defined variable，
#然后每次下去都按照你已经写好的那部分迭代，差不多就是酱紫。

#无用function还有match的问题都可以用problem1的代码

def assign_node_check(node,defined_variables):
    all_undefined_Use=0
    if isinstance(node.value, ast.Name):#如果右边是简单的一个变量，那么就check这个变量有没有define
        if node.value.id in defined_variables:#如果右边的variable已经define了，那么左边的就可以加到defined variable里面去
            defined_variables.add(node.targets[0].id)
        else:#如果右边没有define，那么找左边的variable看在不在define里面，在的话就删除，不在的话就不做操作。无论在不在，use=use+1
            if node.targets[0].id in defined_variables:
                defined_variables.remove(node.targets[0].id)
                
            all_undefined_Use=all_undefined_Use+1
    elif isinstance(node.value, ast.Constant):#如果右边是简单的一个常数，那么check左边的target在不在define里面，在就不变，不在就加到define里面(tester2实验以后发现添加的话直接加就行了)
        defined_variables.add(node.targets[0].id)


    else:#如果右边是一个嵌套的赋值语句，不是简单一个变量，那么往下找到所有的variable加到一个temp_set中
        temp_set=set()
        for sub_node in ast.walk(node.value):
            if isinstance(sub_node, ast.Name):
                temp_set.add(sub_node.id)

        
        #如果temp set里面什么都没有，那么就说明全是constant，那么左边的variable就加到defined里面去
        if len(temp_set)==0:
            defined_variables.add(node.targets[0].id)
        else:#如果有东西
            The_intersection_set=defined_variables.intersection(temp_set)
            if The_intersection_set==temp_set:#如果东西全在defined里面，那么左边的target就是defined
                defined_variables.add(node.targets[0].id)
            else:#如果有东西undefined，那么左边的就是undefined如果在set里面就要删掉，use=use+len(temp_set-defined_variable)
                if node.targets[0].id in defined_variables:
                    defined_variables.remove(node.targets[0].id)
                
                all_undefined_Use=all_undefined_Use+len(temp_set-defined_variables)
    return all_undefined_Use,defined_variables



def visit_func_node_layer(Node_function_to_check, transformed_defined_variables,defined_variables):
    all_undefined_Use=0
    for node in Node_function_to_check:#如果body剩下还有node，那么把node全部跑完
        Node_to_check=node#取出来下一个node
        if isinstance(Node_to_check, ast.Assign):#如果这个node是assign，执行assign
            use_to_add,new_defined_set=assign_node_check(Node_to_check, transformed_defined_variables)
            all_undefined_Use=all_undefined_Use+use_to_add
            transformed_defined_variables=new_defined_set
        elif isinstance(Node_to_check, ast.FunctionDef):#如果是function_def,暂时先没用#而且testcase里没有嵌套def function
            pass
        else:#只能是被call了，嵌套call

        #把call和function的definition联系起来
            match_func_definitions=[function for function in function_def if function[0]==Node_to_check.value.func.id]#先筛选出名字一样的#注意这里是浅拷贝

            
            Func_list_to_sort=[function for function in match_func_definitions if function[1]<Node_to_check.lineno]#只有def在call之前的才会被call
            #应该一定有这样的function定义

            #有名字一样的，找到line在之前第一个的（也就是sort找lino最大的）
            Func_list_to_sort.sort( key=lambda x: x[1], reverse=True)
            function_to_use=Func_list_to_sort[0]
            Node_function_to_check=function_to_use[2].body#拿出function的body

            variable_name_in_function=[]#找到所有的function_variable的名字
            for arg_node in function_to_use[2].args.args:
                variable_name_in_function=variable_name_in_function+[[arg_node.arg,0,0]]#第一个0代表着没有被call里面改动过，1代表改动了，用来在后面让没改动的可以被default变成defined
                                                                                        #第二个0代表着是defined还是没defined，0代表没define，1代表define了
                                                                                        #最后把global和没defined的减掉（如果里面存在的话，加上defined

            #call的positional部分 #注意到positional和keyword正常程序是不能重复的
            iterate_number=0
            for argument in Node_to_check.value.args:#这里右边也可能是表达式
                #如果是name
                if isinstance(argument, ast.Name):
                    if argument.id in transformed_defined_variables:#改动了，define了
                        variable_name_in_function[iterate_number][1]=1
                        variable_name_in_function[iterate_number][2]=1
                    else:#不然就是改动了，没define。在最后合成新的defined variable的时候要注意
                        variable_name_in_function[iterate_number][1]=1
                        variable_name_in_function[iterate_number][2]=0
                else: #isinstance(argument, ast.Constant):#constant怎么样都是define了
                    variable_name_in_function[iterate_number][1]=1
                    variable_name_in_function[iterate_number][2]=1
                iterate_number=iterate_number+1
                
            #keywords部分
            for keyword in Node_to_check.value.keywords:
                if isinstance(keyword.value,ast.Name):#如果类型是名字的话
                    if keyword.value.id in transformed_defined_variables:#如果在defined variable里，改变了，define了。
                        ##search in the variable_name_in_function list
                        for instance in variable_name_in_function:
                            if instance[0]==keyword.arg:
                                variable_name_in_function[iterate_number][1]=1
                                variable_name_in_function[iterate_number][2]=1
                    else:#那么就是改动了，没define
                        for instance in variable_name_in_function:
                            if instance[0]==keyword.arg:
                                variable_name_in_function[iterate_number][1]=1
                                variable_name_in_function[iterate_number][2]=0
                else:#只剩下constant类型，这里先不考虑那种右边是个表达式的情况。剩下的情况就是这个类型是constant
                    for instance in variable_name_in_function:
                        if instance[0]==keyword.arg:
                            variable_name_in_function[iterate_number][1]=1
                            variable_name_in_function[iterate_number][2]=1#改动了，define了
            #function def自己也会有default内容
            default_iterate=0
            total_variable_length=len(variable_name_in_function)-1
            for default in function_to_use[2].args.defaults:
                if variable_name_in_function[total_variable_length-default_iterate][1]==0:#0代表着没有被改过，没改过的就可以被default改，变成default
                    variable_name_in_function[total_variable_length-default_iterate][2]=1
                default_iterate=default_iterate+1
            

            #把所有没define的做成一个set
            undefine_function_variable=set()
            for variable_name in variable_name_in_function:
                if variable_name[2]==0:#如果没有define，那么就加到undefined的set中
                    undefine_function_variable.add(variable_name[0])
            #把transform先和define相等，然后去掉undefine的，再加上define的
            transformed_defined_variables=defined_variables.copy()
            transformed_defined_variables.difference_update(undefine_function_variable)
            for variable_name in variable_name_in_function:
                if variable_name[2]==1:#如果define，那么就加到新的set中
                    transformed_defined_variables.add(variable_name[0]) 

            

            use_to_add=visit_func_node_layer(Node_function_to_check, transformed_defined_variables,defined_variables)#defined_variable是给嵌套调用使用的
            all_undefined_Use=all_undefined_Use+use_to_add

    return all_undefined_Use

def visit_first_node_layer(current_body):#这个要求有最初defined，每遇到function call就进去一个node_layer
    
    all_undefined_Use=0
    defined_variables=set()
     #这个实际上是node list
    for node in current_body:#如果body剩下还有node，那么把node全部跑完
        Node_to_check=node#取出来下一个node
        if isinstance(Node_to_check, ast.Assign):#如果这个node是assign，执行assign
            use_to_add,new_defined_set=assign_node_check(Node_to_check, defined_variables)
            all_undefined_Use=all_undefined_Use+use_to_add
            defined_variables=new_defined_set
        elif isinstance(Node_to_check, ast.FunctionDef):#如果是function_def,暂时先没用
            pass
        else:#只能是被call了

            #把call和function的definition联系起来
            match_func_definitions=[function for function in function_def if function[0]==Node_to_check.value.func.id]#先筛选出名字一样的#注意这里是浅拷贝

            
            Func_list_to_sort=[function for function in match_func_definitions if function[1]<Node_to_check.lineno]#只有def在call之前的才会被call
            #应该一定有这样的function定义

            #有名字一样的，找到line在之前第一个的（也就是sort找lino最大的）
            Func_list_to_sort.sort( key=lambda x: x[1], reverse=True)
            function_to_use=Func_list_to_sort[0]
            Node_function_to_check=function_to_use[2].body#拿出function的body

            variable_name_in_function=[]#找到所有的function_variable的名字
            for arg_node in function_to_use[2].args.args:
                variable_name_in_function=variable_name_in_function+[[arg_node.arg,0,0]]#第一个0代表着没有被call里面改动过，1代表改动了，用来在后面让没改动的可以被default变成defined
                                                                                        #第二个0代表着是defined还是没defined，0代表没define，1代表define了
                                                                                        #最后把global和没defined的减掉（如果里面存在的话，加上defined

            #call的positional部分 #注意到positional和keyword正常程序是不能重复的
            iterate_number=0
            for argument in Node_to_check.value.args:
                #如果是name
                if isinstance(argument, ast.Name):
                    if argument.id in defined_variables:#改动了，define了
                        variable_name_in_function[iterate_number][1]=1
                        variable_name_in_function[iterate_number][2]=1
                    else:#不然就是改动了，没define。在最后合成新的defined variable的时候要注意
                        variable_name_in_function[iterate_number][1]=1
                        variable_name_in_function[iterate_number][2]=0
                else: #isinstance(argument, ast.Constant):#constant怎么样都是define了
                    variable_name_in_function[iterate_number][1]=1
                    variable_name_in_function[iterate_number][2]=1
                iterate_number=iterate_number+1
                
            #keywords部分
            for keyword in Node_to_check.value.keywords:
                if isinstance(keyword.value,ast.Name):#如果类型是名字的话
                    if keyword.value.id in defined_variables:#如果在defined variable里，改变了，define了。
                        ##search in the variable_name_in_function list
                        for instance in variable_name_in_function:
                            if instance[0]==keyword.arg:
                                variable_name_in_function[iterate_number][1]=1
                                variable_name_in_function[iterate_number][2]=1
                    else:#那么就是改动了，没define
                        for instance in variable_name_in_function:
                            if instance[0]==keyword.arg:
                                variable_name_in_function[iterate_number][1]=1
                                variable_name_in_function[iterate_number][2]=0
                else:#只剩下constant类型，这里先不考虑那种右边是个表达式的情况。剩下的情况就是这个类型是constant
                    for instance in variable_name_in_function:
                        if instance[0]==keyword.arg:
                            variable_name_in_function[iterate_number][1]=1
                            variable_name_in_function[iterate_number][2]=1#改动了，define了
            #function def自己也会有default内容
            default_iterate=0
            total_variable_length=len(variable_name_in_function)-1
            for default in function_to_use[2].args.defaults:
                if variable_name_in_function[total_variable_length-default_iterate][1]==0:#0代表着没有被改过，没改过的就可以被default改，变成default
                    variable_name_in_function[total_variable_length-default_iterate][2]=1
                default_iterate=default_iterate+1
            

            #把所有没define的做成一个set
            undefine_function_variable=set()
            for variable_name in variable_name_in_function:
                if variable_name[2]==0:#如果没有define，那么就加到undefined的set中
                    undefine_function_variable.add(variable_name[0])
            #把transform先和define相等，然后去掉undefine的，再加上define的
            transformed_defined_variables=defined_variables.copy()
            transformed_defined_variables.difference_update(undefine_function_variable)
            for variable_name in variable_name_in_function:
                if variable_name[2]==1:#如果define，那么就加到新的set中
                    transformed_defined_variables.add(variable_name[0]) 

            

            use_to_add=visit_func_node_layer(Node_function_to_check, transformed_defined_variables,defined_variables)#defined_variable是给嵌套调用使用的
            all_undefined_Use=all_undefined_Use+use_to_add
    return all_undefined_Use



#main operation
#remove the unused function in the function
source=remove_unused_functions(source)


#source剩下的都是会被运行的代码
tree=ast.parse(source)
main_body=tree.body

function_def=find_function_definitions(source)
Overall_undefined_Use=visit_first_node_layer(main_body)

print(Overall_undefined_Use)

# print(ast.dump(tree,indent=4))

