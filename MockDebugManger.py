# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2021/12/29
:file: use for debug functions
'''

from Public.Singleton import CommonManagerBase
from MockDebugModule import MockDebugModule
from FuncDecoratorHelper.FuncHandle import MockFuncManager
from DebugStreamMeta.StreamMetaManger import StreamMetaManager
from Debug.MockDebug.MockConst import MockDebugConfig


class DebugManger(CommonManagerBase):

	# manger to handle all module
	# 应该是管理每个模块 然后每个模块各自去管理node
	def __init__(self):
		self.collectionModules = set() # type collection
		super(DebugManger, self).__init__()

	def GetCollectionDebugModule(self):
		self.Close() # 先不支持多个流吧
		for streamName in MockDebugConfig.MODULES:
			streamMetaCls = StreamMetaManager.Instance().GetStream(streamName)
			if streamMetaCls:
				context = {}
				streamMetaObj = streamMetaCls(context)
				module = MockDebugModule(streamName, streamMetaObj)
				self.collectionModules.add(module)

	def Start(self):
		print("MOCK_START")
		self.GetCollectionDebugModule()

	def Close(self):
		import linecache
		linecache.clearcache() # 清楚line
		print("MOCK_STOP")
		for m in self.collectionModules:
			m.ReleaseDebug()
		self.collectionModules = set()
		MockFuncManager.Clear()
		StreamMetaManager.Instance().Clear()
