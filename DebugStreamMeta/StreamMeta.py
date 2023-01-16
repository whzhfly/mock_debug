# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2021/12/29
:file: use for debug functions
'''

from StreamMetaManger import StreamMetaClass
from StreamNodeMeta import TmpGetNode # 后面改成获取
from Debug.MockDebug.MockConst import Tags

LETriggerContainer = "LETriggerContainer"

class StreamLoggerEnum(object):

	DEFAULT = 0
	TRIGGER = 1
	SEQUENCE = 2


class StreamMetaBase(object):
	"""
	general meta
	use for debug nodes
	"""

	__metaclass__ = StreamMetaClass
	_reload_all = True

	STREAM_LOGGER = 0
	STREAM_TEXT = ""

	def __init__(self, context=None):
		self.stream = {}
		self.context = context
		self.Init()

	def Init(self):
		nodesFunctions = self.LoadStreamFunctions()
		if nodesFunctions:
			# [(obj,func,name),()]
			for node in nodesFunctions:
				# 统一
				self.GenNodes(*node)

	def LoadStreamFunctions(self):
		return None

	def GetStreamNodes(self):
		# 获取stream中的node
		# return 一个 set()
		se = set()
		for v in self.stream.values():
			se.add(v)
		return se

	def GetStream(self):
		# 获取这个流信息
		return self.stream

	def GenNodes(self, rawNode, funcs=None, name=None):
		streamNode = TmpGetNode(rawNode, name) # 使用默认的 去修饰
		if streamNode:
			streamNode.SetFilter(funcs) # setfilter
			streamNode.SetName(rawNode.__name__)
			streamNode.Start()
			self.stream[rawNode.__name__] = streamNode

	def GetAllFuncs(self):
		funcs = set()
		for st in self.stream.values():
			funcs.update(st.GetNodeFuncs())
		return funcs

	def GetStreamLoggerType(self):
		return StreamLoggerEnum.DEFAULT

	def CallStreamLocalFilter(self, event):
		"""
		用于call和return时候的的回调
		"""
		if event.tags == Tags.CALL_TAG:
			# return的时候 self.entity 可能是 None
			# setfilter 应该在进入的时候set
			self.SetFilterContext(event)
		return self.OnEventStreamCallBack(event)

	def OnEventStreamCallBack(self, event):
		# 子类的回调
		return True

	def SetFilterContext(event):
		pass

class SequenceStream(StreamMetaBase):
	"""
	序列式stream,当hook的函数被触发的时候，会检测一下是否有初始函数被激活
	只有初始函数被激活，才会记录hook函数的logger信息
	主要是FirstFunc的概念
	"""

	def GetStreamLoggerType(self):
		return StreamLoggerEnum.SEQUENCE

	def GetFirstFunc(self):
		"""
		返回指定的初始函数
		"""
		return None

class TriggerStream(StreamMetaBase):
	'''
	每一个hook的函数都是FirstFunc
	'''

	def GetStreamLoggerType(self):
		return StreamLoggerEnum.TRIGGER
