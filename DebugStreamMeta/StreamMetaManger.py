# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2022/01/04
:file: use for
'''

from Public.Singleton import CommonManagerBase
from GUtils import CommonUtil


class StreamMetaManager(CommonManagerBase):
	def __init__(self):
		super(StreamMetaManager, self).__init__()
		self.streamCache = {}
		self.ImpAllModule()

	def ImpAllModule(self):
		CommonUtil.ImportModuleByDir(["Debug", "MockDebug", "DebugStreamMeta"]) # 可以用简单的import

	def RegStream(self, name, newcls):
		self.streamCache[name] = newcls

	def GetStream(self, name):
		# print("GetStreamGetStream", self.streamCache)
		return self.streamCache.get(name)

	def Clear(self):
		# 重新载入
		# self.self.streamCache = {}
		pass

	def GetStreamTextData(self):
		return {k: v.STREAM_TEXT for k, v in self.streamCache.items() if v.STREAM_TEXT}

class StreamMetaClass(type):
	"""
	meta class
	"""
	def __new__(mcs, name, bases, attrs):
		newCls = super(StreamMetaClass, mcs).__new__(mcs, name, bases, attrs)
		StreamMetaManager.Instance().RegStream(name, newCls)
		return newCls
