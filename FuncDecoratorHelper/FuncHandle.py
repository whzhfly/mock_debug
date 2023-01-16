# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2021/12/29
:file: use prase to get a new function code
'''


from Public.Singleton import CommonManagerBase
import inspect
from MagicFunctions import MagicFuncs
from AstHandle import MagicAstHelper

_reload_all = True


class MockManager(CommonManagerBase):
	"""
	用于保存分析得到的函数
	"""
	def __init__(self):
		super(MockManager, self).__init__()
		self.expressionCache = {}
		self.func2WarpFunc = {}
		self.funcCode2Source = {}
		self.func2Code2CallBack = {} # 使用callback 就不直接对象引用了

	def GetWarpFunc(self, func, eventCallBack):
		if func in self.func2WarpFunc:
			# print("GetWarpFuncGetWarpFunc", self.func2WarpFunc)
			# for k,v in self.func2WarpFunc.iteritems():
			# 	print("GetWarpFuncGetWarpFunciteritems", k, v.__globals__["SOURCE_FILE"])
			return self.func2WarpFunc[func]
		else:
			newFunc, SOURCE_FILE = self.GenRealFunc(func)
			self.func2WarpFunc[func] = newFunc
			self.funcCode2Source[newFunc.func_code] = SOURCE_FILE
			self.func2Code2CallBack[newFunc.func_code] = eventCallBack
			return newFunc

	def Clear(self):
		self.expressionCache = {}
		self.func2WarpFunc = {}
		self.funcCode2Source = {}
		self.func2Code2CallBack = {}

	# def GenRealFunc(self, func):
	# 	funcSource = inspect.getsource(func)
	# 	newSource, newTree = MagicAstHelper(funcSource, func)
	# 	import copy
	# 	SOURCE_FILE = copy.deepcopy(newSource)
	# 	g = {"SOURCE_FILE": SOURCE_FILE} # 可见这里的SOURCE_FILE 改变了现在
	# 	g.update(MagicFuncs)

	# 	g.update(func.__globals__)
	# 	exec(SOURCE_FILE, None, g)
	# 	newFunc = g[func.__name__]
	# 	print "GenRealFunc",func,SOURCE_FILE
	# 	s = newFunc.__globals__
	# 	print "SOURCE_FILE"
	# 	s.update(g) # 或许这里把SOURCE_FILE 覆盖到了 s 而s 是__globals__
	# 	return newFunc

	def GenRealFunc(self, func):
		funcSource = inspect.getsource(func)
		# 有个问题 如果手动的reload这里的函数 这里没有reload 或许是reload 没有修改文件？？
		# print(inspect.getsource(USpellCtrl.CheckSpellCost))
		# 如果现在手动的在 CheckSpellCost 添加信息 这里的getsourc还是原来的文本
		# 大概率是 inspect.getsourc 这个方法无法获取reload 后的东西 可能是没有替换的原因
		# 所有后面可以自己实现这个方法 获取真正的函数
		newSource, newTree = MagicAstHelper(funcSource, func)
		import copy
		SOURCE_FILE = copy.deepcopy(newSource)
		# print("getNewSource", newSource)
		sourceDict = {"SOURCE_FILE": SOURCE_FILE} # 可见这里的SOURCE_FILE 改变了现在

		g = {}
		g.update(MagicFuncs)
		g.update(func.__globals__)
		exec(SOURCE_FILE, None, g)

		newFunc = g[func.__name__]
		s = newFunc.__globals__

		s.update(g)
		s.update(sourceDict)
		return newFunc, SOURCE_FILE

MockFuncManager = MockManager.Instance()
