# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2021/12/29
:file: some easy decorators
'''


import inspect
from FuncHandle import MockFuncManager
from functools import wraps

class DecoratorManger(object):
	@staticmethod
	def GetAllDecorators():
		res = {}
		for varName, varObj in globals().iteritems():
			if varName.startswith("_"):
				continue
			if inspect.isclass(varObj):
				for attrName, attrValue in varObj.__dict__.iteritems():
					if attrName.startswith("_"):
						continue
					if attrName == "GetAllDecorators":
						continue
					if attrName == "DebugLocalDecorator":
						continue
					if isinstance(attrValue, staticmethod) or isinstance(attrValue, classmethod):
						res[attrName] = getattr(varObj, attrName, None)
		return res

class DebugDecoratorBase(object):
	"""
	静态的修饰表示开始
	"""
	@staticmethod
	def DebugFunc(func, LOGGER):
		LOGGER.append("DebugFuncStart")
		return func


class DebugLocalDecorator(DebugDecoratorBase):
	"""
	获取函数对应的locals
	"""
	@staticmethod
	def DebugLocal(func, eventCallBack):
		@wraps(func if not (isinstance(func, staticmethod) or isinstance(func, classmethod)) else func.__func__)
		def MockCallFunc(*args, **kwargs):
			warpFunc = MockFuncManager.GetWarpFunc(func, eventCallBack)
			# print "funcfuncfunc",func,func.__name__
			# print "warpFuncwarpFuncwarpFunc",warpFunc,warpFunc.__name__
			res = warpFunc(*args, **kwargs)
			return res
		return MockCallFunc

	@staticmethod
	def DebugNewFunc(func, eventCallBack):
		newFunc = MockFuncManager.GetWarpFunc(func, eventCallBack)
		# print "funcfuncfunc",func,func.__name__
		# print "warpFuncwarpFuncwarpFunc",newFunc,newFunc.__name__
		return newFunc
