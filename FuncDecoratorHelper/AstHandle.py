# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2021/12/29
:file: 为什么这么多static
'''

import ast
# import astunparse
from Debug.LittleYellowDuck import astunparse

def MagicAstHelper(code, func):
	newCode = WarpFunc1(code, func)
	source, tree = AstHandleHelper.Wokr(newCode)
	return source, tree

def WarpFunc1(code, func):
	# 在新的module 中 他不是类的函数 只能是一个def
	# 他的def 是没有缩进的
	# 要把原来的缩进去掉
	rawIndent, funcIndent = GetLineIndent(code)
	newLines = ""
	for line in code.splitlines():
		newLines += line[rawIndent:] +'\n' # 要把原来的缩进取消
	return newLines

def GetLineIndent(line):
	fakeLine = line
	indent = 0
	while(fakeLine[0] == '\t'):
		indent += 1
		fakeLine = fakeLine[1:]
	return indent, indent*'\t'

class MagicCallFuncHelper(object):

	@staticmethod
	def GetArgCallNode():
		codeS = "ArgCall()"
		code = ast.parse(codeS)
		return code.body[0]

	@staticmethod
	def GetAddReturnNone():
		codeS = "PPReturn() #Last_Auto_Add"
		code = ast.parse(codeS)
		return code.body[0]

class AstHandleHelper(object):
	'''
	用来改变一个ast
	确保 code 里面第一个是func
	'''

	@staticmethod
	def Wokr(code):
		code = ast.parse(code)
		funcNode = code.body[0]
		AstHandleHelper.AddBegin(funcNode)
		AstHandleHelper.AddEnd(funcNode)
		newTree = AstHandleHelper.VisitReturn(funcNode)
		newSource = astunparse.unparse(newTree)
		return newSource, newTree

	@staticmethod
	def AddBegin(funcNode):
		funcNode.body.insert(0, MagicCallFuncHelper.GetArgCallNode())

	@staticmethod
	def AddEnd(funcNode):
		funcNode.body.append(MagicCallFuncHelper.GetAddReturnNone())

	@staticmethod
	def VisitReturn(code):
		astNode = code
		myVisitor = WarpVisitor()
		newAst = myVisitor.visit(astNode)
		new_tree = ast.fix_missing_locations(newAst)
		return new_tree

class WarpVisitor(ast.NodeTransformer):
	def __init__(self):
		super(WarpVisitor, self).__init__()

	def visit_Return(self, node):
		# 因为这里有一个GetAddReturnNone 所以也不好分到另一文件
		# 后面在处理
		return [MagicCallFuncHelper.GetAddReturnNone(), self.generic_visit(node)]
