import javalang

MEMBER_REFERENCE = javalang.tree.MemberReference
THIS = javalang.tree.This
ASSIGNMENT = javalang.tree.Assignment
SUPER_CONSTRUCTOR_INVOCATION = javalang.tree.SuperConstructorInvocation
EXPLICIT_CONSTRUCTOR_INVOCATION = javalang.tree.ExplicitConstructorInvocation
METHOD_INVOCATION = javalang.tree.MethodInvocation
RETURN_STATEMENT = javalang.tree.ReturnStatement
STATEMENT_EXPRESSION = javalang.tree.StatementExpression
THROW_STATEMENT = javalang.tree.ThrowStatement
IF_STATEMENT = javalang.tree.IfStatement
LOCAL_VARIABLE_DECLARATION = javalang.tree.LocalVariableDeclaration
BINARY_OPERATION = javalang.tree.BinaryOperation

TYPE = tuple([MEMBER_REFERENCE, THIS, ASSIGNMENT, SUPER_CONSTRUCTOR_INVOCATION, EXPLICIT_CONSTRUCTOR_INVOCATION
        , METHOD_INVOCATION, RETURN_STATEMENT, STATEMENT_EXPRESSION,THROW_STATEMENT])

INCREASE_FILTERATION_STRENGTH = True
FILTER_TOKENS = 3

def set_increase_filteration_strength(input: bool):
    global INCREASE_FILTERATION_STRENGTH
    INCREASE_FILTERATION_STRENGTH = input

def set_filter_tokens(input: int):
    global FILTER_TOKENS
    FILTER_TOKENS = input

def is_binary_operation(item):
    if hasattr(item, 'expression'):
        if isinstance(item.expression, BINARY_OPERATION):
            return True
    return False


def filter_expression_and_expressionl(item, set):
    if hasattr(item, 'expression'):
        if not isinstance(item.expression, TYPE):
            return False
        if hasattr(item.expression, 'expressionl'):
            # 如果if语句下的内容不在白名单中，则返回False，不应被过滤
            if not isinstance(item.expression.expressionl, TYPE):
                return False
    if not isinstance(item, (RETURN_STATEMENT, THROW_STATEMENT)):
        set.add(type(item))
    return True


def filter_if(item,set):
    if isinstance(item, javalang.tree.IfStatement):
        # 遍历if语句中的内容
        if isinstance(item.then_statement, RETURN_STATEMENT):
            #set.add(type(item))
            return True
        if hasattr(item.then_statement, 'statements'):
            for item2 in item.then_statement.statements:
                # 嵌套if,不过滤
                if isinstance(item2, IF_STATEMENT):
                    set.add(type(item2))
                    return False
                # 是返回语句
                if isinstance(item2, RETURN_STATEMENT):
                    if is_binary_operation(item2):
                        return False
                    #set.add(type(item2))
                    continue
                elif isinstance(item2, THROW_STATEMENT):
                    #set.add(type(item2))
                    continue
                result = filter_expression_and_expressionl(item2,set)
                if result is False:
                    return result
        # 遍历else语句中的内容
        if item.else_statement is not None:
            if isinstance(item.else_statement, javalang.tree.IfStatement):
                return filter_if(item.else_statement,set)
            else :
                if isinstance(item.then_statement, RETURN_STATEMENT):
                    #set.add(type(item))
                    return True
                if hasattr(item.else_statement, 'statements'):
                    for item2 in item.else_statement.statements:
                        if isinstance(item2, RETURN_STATEMENT):
                            #set.add(type(item2))
                            continue
                        elif isinstance(item2, THROW_STATEMENT):
                            #set.add(type(item2))
                            continue
                        result = filter_expression_and_expressionl(item2,set)
                        if result is False:
                            return result
        return True


# body 为空
# body[0] 是 SuperConstructorInvocation : 调用父类构造方法语句
# body[0] 是 StatementExpression, expression 是 Assignment, expressionl 是 MemberReference: 成员变量赋值语句
# body[0] 是 StatementExpression, expression 是 Assignment, expressionl 是 This: 成员变量赋值语句
# body 是 ReturnStatement : 返回语句
# body 只有一个， body[0] 是 StatementExpression, expression 是 Assignment ： 赋值语句
# body 只有一个， body[0] 是 StatementExpression, expression 是 ExplicitConstructorInvocation ： 显示构造方法调用语句
# body 是一个 try-catch 且 try 中只有一句语句调用
# if嵌套均不过滤
def ffilter(node):
    """
    用在find函数中, 当发现node属于上述语句时,返回True,否则返回False
    """
    # 空结构体
    cnt=0
    temp_type_set = set()
    if len(node.body) == 0:
        return True
    if len(node.body) == 1:
        # 只有一种语句
        if isinstance(node.body[0], javalang.tree.IfStatement):
            return filter_if(node.body[0], temp_type_set)
        # 只有返回语句
        if isinstance(node.body[0], RETURN_STATEMENT):
            if is_binary_operation(node.body[0]):
                return False
            return True
        elif isinstance(node.body[0], THROW_STATEMENT):
            return True
        elif isinstance(node.body[0], STATEMENT_EXPRESSION):
            # 只有赋值语句
            if isinstance(node.body[0].expression, ASSIGNMENT):
                return True
            # 只有调用构造方法语句
            elif isinstance(node.body[0].expression, EXPLICIT_CONSTRUCTOR_INVOCATION):
                return True
            # 只有方法调用
            elif isinstance(node.body[0].expression, METHOD_INVOCATION):
                return True
            # 只有SUPER调用
            elif isinstance(node.body[0].expression, SUPER_CONSTRUCTOR_INVOCATION):
                return True
        # try语句
        elif isinstance(node.body[0], javalang.tree.TryStatement):
            # try 中语句小于等于 1 条
            if len(node.body[0].block) <= 1:
                return True
        return False
    if len(node.body) != 1 and INCREASE_FILTERATION_STRENGTH:
        for item in node.body:
            # 是if语句下的this赋值语句
            if isinstance(item, javalang.tree.IfStatement):
                #temp_type_set.add(IF_STATEMENT)
                result = filter_if(item,temp_type_set)
                # 如果前面没有返回False,说明if语句内容应该被过滤
                if result is True:
                    cnt += 1
                else :
                    return result      
            elif isinstance(item, RETURN_STATEMENT):
                cnt += 1
                #temp_type_set.add(RETURN_STATEMENT)
            elif isinstance(item, LOCAL_VARIABLE_DECLARATION):
                cnt += 1
                temp_type_set.add(LOCAL_VARIABLE_DECLARATION)
            # 如果item有expression这个属性,则继续判断
            elif hasattr(item, 'expression'):
                # 如果body中的所有item不全是上述语句,则返回False,如果全是，返回True
                if isinstance(item.expression, SUPER_CONSTRUCTOR_INVOCATION):
                    temp_type_set.add(SUPER_CONSTRUCTOR_INVOCATION)
                    cnt+=1
                elif isinstance(item.expression, ASSIGNMENT):
                    if isinstance(item.expression.expressionl, MEMBER_REFERENCE):
                        temp_type_set.add(MEMBER_REFERENCE)
                        cnt+=1
                    elif isinstance(item.expression.expressionl, THIS):
                        temp_type_set.add(THIS)
                        cnt+=1
                elif isinstance(item.expression, EXPLICIT_CONSTRUCTOR_INVOCATION):
                    temp_type_set.add(EXPLICIT_CONSTRUCTOR_INVOCATION)
                    cnt+=1
                elif isinstance(item.expression, RETURN_STATEMENT):
                    if is_binary_operation(item.expression):
                        return False
                    #temp_type_set.add(RETURN_STATEMENT)
                    cnt+=1 
                elif isinstance(item.expression, THIS):
                    temp_type_set.add(THIS)
                    cnt+=1
                elif isinstance(item.expression, METHOD_INVOCATION):
                    temp_type_set.add(METHOD_INVOCATION)
                    cnt+=1
        # 如果body中的所有item不全是上述语句,则返回False,如果全是，返回True
        if cnt == len(node.body) and len(temp_type_set) < FILTER_TOKENS :
            return True
        else :
            return False