# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2022/01/05
:file: a general logger output
'''

from Debug.MockDebug.MockConst import MockDebugConfig
import time

def SetForce(flag):
	ModuleLogger.FORCE_MODEL = flag


LIMIT = 10000

class StreamLoggerEnum(object):

	DEFAULT = 0
	TRIGGER = 1
	SEQUENCE = 2

class Tags(object):
	RETURN_TAG = 1
	CALL_TAG = 2

class ModuleLogger(object):

	FORCE_MODEL = False
	COUNT = 0

	def __init__(self, moduleName, moduleMeta):
		self.moduleName = moduleName
		self.moduleMeta = moduleMeta
		self.streamLock = False # 用来开启锁
		self.loggerCollection = {}

		self.logStack = []
		self.firstNum = 0
		self.filterContext = None
		self.InitFunc()

	def InitFunc(self):
		self.moduleLoggerType = self.moduleMeta.GetStreamLoggerType()
		self.sequenceFirstFuncs = []
		if self.moduleLoggerType == StreamLoggerEnum.SEQUENCE:
			self.funcs = self.moduleMeta.GetAllFuncs()
			self.sequenceFirstFuncs = self.moduleMeta.GetFirstFunc() or []

	def EventAddLogger(self, event):
		if ModuleLogger.COUNT >= LIMIT:
			# 防止log 太多 卡主
			return
		if self.moduleLoggerType == StreamLoggerEnum.TRIGGER:
			self.SequenceHandle(event)
		elif self.moduleLoggerType == StreamLoggerEnum.SEQUENCE:
			self.SequenceHandle(event)

	def SequenceHandle(self, event):
		nodeFuncName = event.debugNode.node.__name__ + '.' + event.funcName # node.func
		if not nodeFuncName:
			print("SequenceHandleSequenceHandleSequenceHandle")
			return
		if self.IsFirstItemInSequcen(nodeFuncName):
			event.context["nodeFuncName"] = nodeFuncName
			self.logStack.append(event.context)
			self.SequenceActive(event)
			return
		elif not self.streamLock:
			return
		else:
			event.context["nodeFuncName"] = nodeFuncName
			self.logStack.append(event.context)

	def IsFirstItemInSequcen(self, funcName):
		if self.moduleLoggerType == StreamLoggerEnum.SEQUENCE:
			return funcName in self.sequenceFirstFuncs
		elif self.moduleLoggerType == StreamLoggerEnum.TRIGGER:
			return True

	def SequenceActive(self, event):
		tag = event.tags
		if tag == Tags.CALL_TAG:
			if self.firstNum == 0:
				self.SetStreamFilter(event.filterContext)
			self.firstNum += 1
			self.streamLock = True
		elif tag == Tags.RETURN_TAG:
			self.streamLock = False
			self.firstNum -= 1
			if self.firstNum == 0:
				self.SequenceFinishe()

	def SetStreamFilter(self, filter):
		self.filterContext = filter

	def SequenceFinishe(self):
		"""
		输出 并重置
		"""
		self.OutPutSequence()
		self.SetStreamFilter(None) # 重置filter
		self.logStack = [] # 重置stack

	def OutPutSequence(self):
		xmlElt = self.GenXmlStack()
		xmlStr = xmlElt.toprettyxml()
		self.SendToAvatar(xmlStr)

	def GenXmlStack(self):
		import xml.dom.minidom
		doc = xml.dom.minidom.Document()
		entElt = doc.createElement(self.moduleName)
		logElts = [entElt]
		curTime = time.time()
		entElt.setAttribute("timestamp", str(curTime))
		for k, v in self.filterContext.iteritems():
			entElt.setAttribute(k, str(v))


		for s in self.logStack:
			# 原来是 __call__ 和 __return__ 会创建
			# 然后locals 信息挂在 __return__ 上

			if s["Tag"] == "_RETURN_":
				head = logElts[-1] # 这个是call 神奇的stack
				# 退出上一个
				# head.setAttribute("LineText", s["line"])
				self.AddLocal(s, head, doc)
				if s.get("xmldoc", None):
					head.appendChild(s["xmldoc"]) # child
				logElts.pop()
			elif s["Tag"] == "_CALL_":
				elt = doc.createElement(s["nodeFuncName"])
				if s["call"]:
					head = logElts[-1]
					head.appendChild(elt)
					logElts.append(elt)
		return entElt

	def AddLocal(self, s, elt, doc):
		"""添加后会比较复杂
		"""
		# return
		# if ModuleLogger.FORCE_MODEL and s["local"]:
		# 	for propKey, prop in s["local"].iteritems():
		# 		propElt = doc.createElement("LocalVariables")
		# 		propElt.setAttribute(str(propKey), repr(prop))
		# 		elt.appendChild(propElt)

		# 试一下不用包装
		if ModuleLogger.FORCE_MODEL and s["local"]:
			index = 0
			for i in s["codefile"]:
				index += 1
				# print(str(index), i)
				elt.setAttribute("LineText"+str(index), i)

			for propKey, prop in s["local"].iteritems():
				# propElt = doc.createElement("LocalVariables")
				elt.setAttribute(str(propKey), repr(prop))
				# elt.appendChild(propElt)
		if not ModuleLogger.FORCE_MODEL:
			elt.setAttribute("LineText", s["line"])

	def SendToAvatar(self, xmlStr):
		avatarId = MockDebugConfig.AvatarId
		if avatarId and self.CheckStreamMask():
			from Core.Entity.EntityManager import EntityManager
			avatar = EntityManager.GetEntity(avatarId)
			avatar.GM.SendMockInfo(xmlStr)
			ModuleLogger.COUNT += 1

	def CheckStreamMask(self):
		mask = MockDebugConfig.FILTER_CONTEXT
		if mask:
			for k, v in self.filterContext.iteritems():
				if k in mask:
					# print("CheckStreamMaskCheckStreamMask" ,k, v, mask[k])
					if str(mask[k]) != str(v):
						return False
		return True
