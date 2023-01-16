# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2021/12/29
:file: use prase to get a new function code
'''

import sys
from Debug.MockDebug.MockConst import EventArgsObj, Tags

_reload_all = True


def GetSource(f_code):
	from FuncHandle import MockFuncManager# 不能互相引用
	so = MockFuncManager.funcCode2Source
	if f_code in so:
		return so[f_code]
	else:
		print("GetSource Falid", so)

def GetCallBack(f_code):
	from FuncHandle import MockFuncManager# 不能互相引用
	so = MockFuncManager.func2Code2CallBack
	if f_code in so:
		return so[f_code]
	else:
		print("GetCallBack Falid", so)
		print("GetCallBack Falid", f_code)

def PPReturn():
	lastFrame = sys._getframe(1)
	# f_code = lastFrame.f_code
	funcSource = GetSource(lastFrame.f_code)
	if not funcSource:
		# 通常是debug结束了
		return
	# fileName = lastFrame.f_code.co_filename
	fileLen = len(funcSource.splitlines())
	lineId = lastFrame.f_lineno
	if lineId >= fileLen:
		lineId = fileLen - 1
	line = funcSource.splitlines()[lineId].replace('\t', '')
	callBackFunc = GetCallBack(lastFrame.f_code)
	funcName = lastFrame.f_code.co_name
	f_local = lastFrame.f_locals
	Tag = "_RETURN_"
	index = lineId
	last4File = []
	while index>1:
		last4File.append(funcSource.splitlines()[index])
		index = index-1
		if lineId - index > 4:
			break
	# print(last4File)
	last4File.reverse()
	context = {"funcName": funcName, "Tag": Tag, "call": False, "local": f_local, "line": line.strip(), "codefile": last4File}
	# print("callBackFunccallBackFunc", callBackFunc)
	if callBackFunc:
		callBackFunc(EventArgsObj(funcName, lastFrame, funcSource, Tags.RETURN_TAG, context))
	return

def ArgCall():
	# print("ArgCallArgCall")
	lastFrame = sys._getframe(1)
	funcSource = GetSource(lastFrame.f_code)
	if not funcSource:
		# 通常是debug结束了
		return
	funcName = lastFrame.f_code.co_name
	Tag = "_CALL_"
	f_local = lastFrame.f_locals
	context = {"funcName": funcName, "Tag": Tag, "call": True, "local": f_local}
	callBackFunc = GetCallBack(lastFrame.f_code)
	# print("callBackFunccallBackFunc", callBackFunc)
	if callBackFunc:
		callBackFunc(EventArgsObj(funcName, lastFrame, None, Tags.CALL_TAG, context))

MagicFuncs = {"PPReturn": PPReturn, "ArgCall": ArgCall}
