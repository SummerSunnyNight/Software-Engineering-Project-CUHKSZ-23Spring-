import ast
import copy

#This function combine all the changes together:
def Problem1(code):
    #Negation:

    code = exchange_comparison_ops(code, ast.Lt, ast.GtE)
    code = exchange_comparison_ops(code, ast.GtE, ast.Lt)
    code = exchange_comparison_ops(code, ast.LtE, ast.Gt)
    code = exchange_comparison_ops(code, ast.Gt, ast.LtE)
 

    code=exchange_operator(code)
    #Remove Unused function
    code=remove_unused_functions(code)

    #Add the global variable
    code=print_global_variables_attheendofthe_code(code)
    return code



#The following are function used to negate the operator

def exchange_operator(code):
    class OperatorExchanger(ast.NodeTransformer):
        def visit_BinOp(self, node):
            if isinstance(node.op, ast.Add):
                return ast.BinOp(left=self.visit(node.left), op=ast.Sub(), right=self.visit(node.right))
            elif isinstance(node.op, ast.Sub):
                return ast.BinOp(left=self.visit(node.left), op=ast.Add(), right=self.visit(node.right))
            elif isinstance(node.op, ast.Mult):
                return ast.BinOp(left=self.visit(node.left), op=ast.Div(), right=self.visit(node.right))
            elif isinstance(node.op, ast.Div):
                return ast.BinOp(left=self.visit(node.left), op=ast.Mult(), right=self.visit(node.right))
            else:
                return node
    root = ast.parse(code)
    exchanger = OperatorExchanger()
    new_root = exchanger.visit(root)
    new_code = ast.unparse(new_root)

    return (new_code)





def exchange_comparison_ops(code, from_op, to_op):
    # Define a transformer class to traverse the AST and exchange comparison operators
    class ComparisonOpTransformer(ast.NodeTransformer):
        def visit_Compare(self, node):
            # Check if the operator matches the one we want to exchange
            if any(isinstance(op, from_op) for op in node.ops):
                # Create a new list of operators with the exchanged operators
                new_ops = []
                for op in node.ops:
                    if isinstance(op, from_op):
                        new_ops.append(to_op())
                    else:
                        new_ops.append(op)

                # Create a new Compare node with the exchanged operators
                new_node = ast.Compare(left=node.left, ops=new_ops, comparators=node.comparators)
                return ast.copy_location(new_node, node)
            else:
                return node

    # Parse the code into an AST
    tree = ast.parse(code)

    # Traverse the AST with the transformer
    transformer = ComparisonOpTransformer()
    new_tree = transformer.visit(tree)

    # Generate new code from the modified AST
    new_code = ast.unparse(new_tree)

    return new_code




#The following are function used to find the variables defined outside of the function definition and print them in the end of the code
def find_variables_defined_outside_functions(code):
    # Parse the code into an AST
    tree = ast.parse(code)

    # Create a set to store the names of all variables defined outside function definitions
    variables_defined_outside_functions = set()

    # Define a visitor class to traverse the AST and extract information about variables
    class VariableVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            # Don't traverse into function definitions
            pass

        def visit_Assign(self, node):
            if not any(isinstance(parent, ast.FunctionDef) for parent in ast.walk(node)):
                # If the assignment occurs outside any function definition, add the variable name to the set
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variables_defined_outside_functions.add(target.id)

    # Traverse the AST with the visitor
    visitor = VariableVisitor()
    visitor.visit(tree)

    return variables_defined_outside_functions

def print_global_variables_attheendofthe_code(code):
    variable_set=find_variables_defined_outside_functions(code)
    for variable in variable_set:
        code=code+'\nprint('+variable+')'

    return code

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

def remove_nodes_from_first_level(tree, nodes_to_remove):
    """
    Removes all nodes from the first level of the given AST tree (root node) based on the given list
    of nodes to remove, and returns the modified AST tree.
    """
    # Iterate over the body of the root node and filter out nodes that are not in the nodes_to_remove list
    tree.body = [node for node in tree.body if node not in nodes_to_remove]
    return tree

    tree=ast.parse(code)





#Testcase3:
# codes='''def func():
#     x = 1
#     y = x >= 0
# y = 100
# x = 6 * y'''

# Testcase5:
# codes='''def func1(y, x=5):
#     x = 0
#     y = y - 2

# m = 1 >= 0
# x = 6 / (6 - m)

# def foo1():
#     y = 1 < 1

# func1(y=m, x=x)'''


#Testcase6
# codes='''def func1(y, x=5):
#     x = 0
#     y = y - 2

# def foo1():
#     y = 1 < 1
#     func1(y, x=4)

# foo1()'''

#Testcase7
# codes='''x = 7.5
# y = x + x*5.5
# def add1():
#     x = x + 1
#     add2(x)
# def add2(y):
#     y = y + 2
#     add3(y)
#     z = y * (5.5 >=2)
# def add3(z):
#     z = z + 3
# add2(y)
# add3(x)'''


#最后提交的时候把这个修改去掉注释
codes = input()
codes = "\n".join(codes.split("\\n"))


tree=ast.parse(codes)

# print(ast.dump(tree,indent=4))

print(Problem1(codes))


#从9点到15点写function detection