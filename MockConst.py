# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2021/12/29
:file: use for debug Const
'''



class MockDebugConfig(object):
	_reload_all = True
	MODULES = ["ActionLineStream"]
	AvatarId = None

	FORCE_MODEL = False
	LIMIT = 10000

	FILTER_CONTEXT = None

class StreamLoggerEnum(object):

	DEFAULT = 0
	TRIGGER = 1
	SEQUENCE = 2

class Tags(object):
	RETURN_TAG = 1
	CALL_TAG = 2


class EventArgsObj(object):

	Filter_Entity = "entity"
	Filter_PrefabId = "prefabId"
	Filter_BehaviorId = "behaviorId"

	def __init__(self, funcName, lastFrame, sourceFile, tags, context):
		self.funcName = funcName # 函数名
		self.lastFrame = lastFrame # frame
		self.sourceFile = sourceFile # 源代码
		self.tags = tags # 标签
		self.context = context # func 传递的信息
		self.debugFunc = None # 对应的func
		self.debugNode = None # 对应的node
		self.debugModule = None # 保存的module
		self.xmldoc = None # xml信息
		self.filterContext = {self.Filter_Entity: None,
			self.Filter_PrefabId: None, self.Filter_BehaviorId: None}
