# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2021/12/29
:file: use for debug functions
'''
from MockDebugFunction import MockDebugFunction
from MockEvent.MockEvent import Event
from FuncDecoratorHelper.MagicFunctions import MagicFuncs

from Tools import funcode_reloader # 依赖


class MockDebugNode(object):
	# 作用于部分node的功能实现
	# 主要实现的是 一个node 中如何获取debug哪些function
	# 为什么有node的概念 理论上流是直接针对func的 但是获取func需要node
	# 而且func可能重名 不过貌似重名也没什么影响

	def __init__(self, moduleName, nodeMeta):
		self.moduleName = moduleName
		self.nodeMeta = nodeMeta
		self.node = nodeMeta.rawNode
		self.debugFuncs = nodeMeta.GetNodeFuncs()
		self.applyFuncs = {} # 真正作用的集合
		self.unAbleWarp = set() # 未能作用的集合
		self.reloadNewFuncToRawFunc = {}

		self.nodeEvent = Event()

	def MockWork(self):
		self.GenDebugFunc()
		self.LockFuncs()

	def GenDebugFunc(self):
		for f in self.debugFuncs:
			mf = MockDebugFunction(f)
			self.RegistEvent(mf)
			funcName = f.__code__.co_name
			self.applyFuncs[funcName] = mf

	def LockFuncs(self):
		LockName = []
		for k, v in MagicFuncs.iteritems():
			import __builtin__
			setattr(__builtin__, k, v)
			# 不是setattr
			# 是吧这个 注入到global里面去
			# 要不用 builtin试试
		# reload 方式问题
		# 这里变了东西

		for k, v in self.applyFuncs.iteritems():
			oldFunc = v.GetRwaFunction()
			newFunc = v.GetWarpFunction()
			if self.node.__dict__[k] == oldFunc:
				LockName.append(oldFunc)

				self.RestoreOldFunc(v, oldFunc, newFunc)
				# setattr(self.node, k, newFunc)
				# 原有的函数存在 hook住 如 patical 之类的无法debug
				# print("dsadasdasdasda")
				# print(oldFunc, newFunc)
				# print(newFunc.func_code)
				# print(oldFunc.func_code)
				funcode_reloader.update_fun(oldFunc, newFunc)
			else:
				# 存在特殊函数获取的名字不太对
				self.unAbleWarp.add(k)
		msg = "LockFunc nodeName=%s funcNames=%s " % (self.node.__name__, str(LockName))
		# print(self.applyFuncs)
		print(msg)

	def RestoreOldFunc(self, v, oldFunc, newFunc):
		# 发现 python的内置对象 不支持 deepcopy 方法
		# 可能只有container 支持
		# 不过相关 functionobj 本质是个指针 或许类似这种的都没有吧
		# 研究发现 运行只要替换__code__ 即可 py3 是 func_code py2 有点丑陋
		# 所以我们把__code__ cache 下来即可
		# 参考下 reloadfunc 中需要保存的
		# import copy
		# deepcopy wrong
		oldCode = oldFunc.__code__
		# print(oldCode)
		v.ReloadSetRawFunction(oldCode)

	def UnLockFuncs(self):
		unLockName = []
		print(self.applyFuncs)
		for k, v in self.applyFuncs.iteritems():
			if k not in self.unAbleWarp:
				curFunc = v.GetRwaFunction()
				# curFunc = getattr(self.node, k).__func__ # 添加__func__
				# print(curFunc)
				# print(rawFunc)
				# # print(curFunc.func_code)
				# # setattr(self.node, k, oldFunc)
				# funcode_reloader.update_fun(curFunc, rawFunc)
				# unLockName.append(rawFunc)
				rawCodeObj = v.GetRawCodeObject()
				# print("UnLockFuncs", curFunc.__code__, rawCodeObj)
				if rawCodeObj is not None:
					curFunc.__code__ = rawCodeObj

		msg = "UnLockFunc nodeName=%s funcNames=%s" % (self.node.__name__, str(unLockName))
		print(msg)
		self.Release()

	def Release(self):
		for debugFunc in self.applyFuncs.values():
			self.UnRegistEvent(debugFunc)
		self.applyFuncs = {}
		self.unAbleWarp = set()
		self.nodeEvent = None

	def RegistEvent(self, debugFunc):
		debugFunc.funcEvent.RegisterFunc(self.NodeFunctionEvent)

	def UnRegistEvent(self, debugFunc):
		debugFunc.funcEvent.UnregisterFunc(self.NodeFunctionEvent)

	def NodeFunctionEvent(self, event):
		# 发送事件到module 设置debugNode
		event.debugNode = self
		if self.nodeMeta.CallNodeLocalFilter(event):
			self.nodeEvent(event)
