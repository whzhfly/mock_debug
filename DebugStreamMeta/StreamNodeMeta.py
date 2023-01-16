# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2021/12/29
:file: use for collec nodes
'''

_reload_all = True

def TmpGetNode(node, name=None):
	# 先简单处理下
	if not name:
		streamNodeName = node.__name__+"Node"
	else:
		streamNodeName = name
	if streamNodeName in globals():
		return globals()[streamNodeName](node)
	else:
		return StreamNodeBase(node)


# 后续会有这种情况
# 在两个流中都引用了同一个object
# 那么这里是否应该是两个nodemeta
# 应该是的 因为运行时应该只有一个node， 但是这个node可以对应多个nodemeta
# 确实可以，但是func却比较棘手
# 还是做成一个nodemeta吧 至于有交互的两个流，我们停掉一个即可

class StreamNodeBase(object):

	NODE_DEFAULTS = [] # 子类去重载

	def __init__(self, node):
		self.rawNode = node
		self.pointFuncs = []
		self.funcs = {}
		self.name = None

	def SetName(self, name):
		self.name = name

	def GetName(self):
		if self.name:
			return self.name
		else:
			return self.rawNode.__name__

	def Start(self):
		for workName, work in self.rawNode.__dict__.iteritems():
			import types
			if not isinstance(work, types.FunctionType):
				continue
			if not callable(work):
				continue
			if workName.startswith("__"):
				# 去除自带的
				continue
			elif self.pointFuncs:
				if workName in self.pointFuncs:
					# 指定集合需要添加相关的过滤信息
					self.funcs[workName] = work
			else:
				# 其他情况下全部加进来
				self.funcs[workName] = work
		# print("StreamNodeStreamNode", self.__class__.__name__, self.funcs)

	def GetNodeFuncs(self):
		# print "GetNodeFuncsGetNodeFuncs", set([v for v in self.funcs.values()])
		return set([v for v in self.funcs.values()])

	def SetFilter(self, pointFuncs):
		self.pointFuncs = pointFuncs

	def Logger(self):
		# 设置logg 等信息
		pass

	def CallNodeLocalFilter(self, event):
		# self.SetFilterContext(event)
		return self.OnEventNodeCallBack(event)

	def OnEventNodeCallBack(self, event):
		lastFrame = event.lastFrame
		locals = lastFrame.f_locals
		funcSelf = locals.get("self", None) or 1
		if funcSelf is None:
			return False
		else:
			return True

class ConditionNode(StreamNodeBase):
	"""
	用于获取普通condition
	"""

	def OnEventNodeCallBack(self, event):
		# lastFrame = event.lastFrame
		# funcName = event.funcName
		# tag = event.tags
		# locals = lastFrame.f_locals
		# funcSelf = locals.get("self", None) or 1
		# if funcSelf is None:
		# 	return False
		# else:
		# 	if funcName == "OnCue" and tag == 1:
		# 		import xml.dom.minidom
		# 		doc = xml.dom.minidom.Document()
		# 		event.context["xmldoc"] = funcSelf.DebugToDomElement(doc)
		# 	return True
		return True

class ActionNode(StreamNodeBase):
	"""
	用于获取普通condition
	"""

	def OnEventNodeCallBack(self, event):
		return True
