# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2021/12/29
:file: use for debug functions
'''

from MockDebugNode import MockDebugNode
from MockEvent.MockEvent import Event
from LoggerHandle.ModuleLogger import ModuleLogger

class MockDebugModule(object):
	# 用于管理一个模块的 所有node
	# 为什么分模块 一个很重要的原因是 存在重复模块的objname 名字是相似的
	# 这种情况下 在热更之后 很难区分这些 比如avatarspellctrl 和 spellctrl的重载func 写在了同一个文件下 很难区分
	# 分模块可以确定每个模块中的node都是固定的
	# 对于lemodule 来说 这个module 管理的就是所有的lenodes
	# 对应一个Stream


	# 本质还是分层简单很多, 便于管理

	def __init__(self, moduleName, streamMeta):
		self.moduleName = moduleName
		self.streamMeta = streamMeta
		self.collectionSets = set() # 保存修饰的 一个leobj
		self.collectionPrecedureNodes = {} # 保存一个name 到 debugleobj的集合 和上面的稍微有点混乱重复

		self.logger = ModuleLogger(moduleName, streamMeta)
		self.moduleEvent = Event()
		self.ModuleMock()

	def ModuleMock(self):
		# print "GetCollectionDebugNodes,", self.streamMeta
		newSet = self.streamMeta.GetStreamNodes()
		oldSet = self.collectionSets
		if newSet or oldSet:
			self.RefreshCollectionSet(newSet, oldSet)

	def RefreshCollectionSet(self, newSet, oldSet):
		# 对每个集合的debug 进行更新
		# node 是一个 classobj
		addSet = newSet - oldSet
		removeSet = oldSet - newSet

		for node in addSet:
			preNode = self.AddDebugProcedure(node) # 如何保存这个是个问题 存到哪个集合中
			self.collectionPrecedureNodes[node.GetName()] = preNode
		for node in removeSet:
			self.RemoveDebugProcedure(node)
			self.collectionPrecedureNodes.pop(node.GetName())

		# msg = "RefreshCollectionSet moduleName=%s addSet=%s, removeSet=%s" % (self.moduleName, addSet, removeSet)
		# print(msg)
		msg = "RefreshCollectionSet moduleName=%s addN=%d, rmNum=%d" % (self.moduleName, len(addSet), len(removeSet))
		print(msg)
		# print("RefreshCollectionSetRefreshCollectionSet", self.collectionPrecedureNodes)
		self.UpdateCollection(newSet)

	def UpdateCollection(self, newSet):
		self.collectionSets = newSet

	def AddDebugProcedure(self, node):
		debugNode = MockDebugNode(self.moduleName, node) # 后面可以通过一个接口 根据name 获取对应的bug方法
		# print("AddDebugProcedure", node, debugNode)
		self.RegistEvent(debugNode)
		debugNode.MockWork()
		return debugNode

	def RemoveDebugProcedure(self, node):
		self.UnRegistEvent(node)
		node.UnLockFuncs()

	def ReleaseDebug(self):
		for k, node in self.collectionPrecedureNodes.iteritems():
			self.RemoveDebugProcedure(node)
		self.collectionSets = set()
		self.collectionPrecedureNodes = {}

	def RegistEvent(self, debugNode):
		debugNode.nodeEvent.RegisterFunc(self.ModuleNodeFunctionEvent)

	def UnRegistEvent(self, debugNode):
		debugNode.nodeEvent.UnregisterFunc(self.ModuleNodeFunctionEvent)

	def ModuleNodeFunctionEvent(self, event):
		# 发送事件到module 设置debugNode
		# event.debugNode = self
		# self.moduleEvent(self, event)
		# 交给具体的输出去处理
		event.debugModule = self
		if self.streamMeta.CallStreamLocalFilter(event):
			self.logger.EventAddLogger(event)
