import javalang
import copy
import math

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
WHILE_STATEMENT = javalang.tree.WhileStatement
SWITCH_STATEMENT = javalang.tree.SwitchStatement

def calculateQ(file:str) -> int:
    # 获取语法树
    with open(file, 'r', encoding="utf-8") as f:
        tree = javalang.parse.parse(f.read())
    for function in tree.types[0].body: # 此处的node是函数
        statementDict = {}
        for node in function.body:
            statementDict = extendDict(statementDict, calculateStatement(node, statementDict))
        Q = sumQ(statementDict)
        print(statementDict)
        print(Q)
        
    return 0

def jisuanshang(function):
    statementDict = {}
    for node in function.body:
        statementDict = extendDict(statementDict, calculateStatement(node, statementDict))
    Q = sumQ(statementDict)
    if Q <= 0.675:
        return True
    else:
        return False



def calculateStatement(node, statementDict):
    tempDict = copy.deepcopy(statementDict)
    # 对IF语句特判
    if isinstance(node, IF_STATEMENT):
        # 具有内部语句
        if node.then_statement is not None:
            # 具有多个内部语句
            if hasattr(node.then_statement, 'statements'):
                for statement in node.then_statement.statements:
                    tempDict = calculateStatement(statement, tempDict)
            else:
                tempDict = calculateStatement(node.then_statement, tempDict)
        if node.else_statement is not None:
            # 具有多个内部语句
            if hasattr(node.else_statement, 'statements'):
                for statement in node.else_statement.statements:
                    tempDict = calculateStatement(statement, tempDict)
            else:
                tempDict = calculateStatement(node.else_statement, tempDict)
    # while语句和for语句
    elif isinstance(node, WHILE_STATEMENT) or isinstance(node, javalang.tree.ForStatement):
        if node.body is not None:
            if hasattr(node.body, 'statements'):
                for statement in node.body.statements:
                    tempDict = calculateStatement(statement, tempDict)
            else:
                tempDict = calculateStatement(node.body, tempDict)
    # try语句
    elif isinstance(node, javalang.tree.TryStatement):
        if node.block is not None:
            for statement in node.block:
                tempDict = calculateStatement(statement, tempDict)
        if node.finally_block is not None:
            for statement in node.finally_block:
                tempDict = calculateStatement(statement, tempDict)
    elif isinstance(node, javalang.tree.BlockStatement):
        if node.statements is not None:
            for statement in node.statements:
                tempDict = calculateStatement(statement, tempDict)
    # 其他语句
    elif isinstance(node, STATEMENT_EXPRESSION):
        tempDict = calculateStatement(node.expression, tempDict)
    elif isinstance(node, SWITCH_STATEMENT):
        if node.cases is not None:
            for case in node.cases:
                if hasattr(case, 'statements'):
                    for statement in case.statements:
                        tempDict = calculateStatement(statement, tempDict)
        else:
            updateDict(tempDict, SWITCH_STATEMENT)
    else:
        if isinstance(node, RETURN_STATEMENT):
            if hasattr(node, 'expression'):
                tempDict = calculateStatement(node.expression, tempDict)
            updateDict(tempDict, RETURN_STATEMENT)
        else:
            updateDict(tempDict, type(node))

    return tempDict

def updateDict(dict, key):
    if key in dict:
        dict[key] += 1
    else:
        dict[key] = 1

def extendDict(dict1, dict2):
    for key in dict2:
        dict1[key] = dict2[key]
    return dict1

def sumQ(statementDict):
    # 计算每一个statement在总statement中的占比
    Q = 0
    sum = 0
    for key in statementDict:
        sum += statementDict[key]
    for key in statementDict:
        px = statementDict[key] / sum
        # 计算px对数
        logpx = math.log(px)

        Q += px * logpx
    return -Q