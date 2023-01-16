# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2021/12/29
:file: use for debug functions
'''
from FuncDecoratorHelper.FunctionDecorators import DebugLocalDecorator
from MockEvent.MockEvent import Event

# 从上到下 比如 node ==》 func 是很自然地调用
# 是一个 三角的接口 上层有下层的引用 上层能直接调用下层的接口
# 但是很多情况 下层需要通知上层 这种情况下
# 首先下层肯定不应该有上层引用， 会出现相互引用的情况，虽然可以处理但是不符合逻辑习惯，每一层应该足够独立
# 【1】通常我们是用第三方来记录这个关系， 比如一个entity 或者 一个dict集合的概念 这是直接的获取对应的对象
# 【2】还有一种方式是通知的方式，这种通常是用事件去处理， 上层稳定的监听一个下层的接口 下层通过接口传递信息到上层
# 【3】是否有第三种方式呢？或者我们中和一下1和2的方式去处理？
# 先用下Event吧

class MockDebugFunction(object):
	'''
	对应的func的获取
	'''

	def __init__(self, rawFunc):
		self.rawFunc = rawFunc
		self.warpFunc = None
		self.funcEvent = Event()
		self.ApplyWarp()
		self.rawCodeObject = None

	def GetWarpFunction(self):
		return self.warpFunc

	def GetRwaFunction(self):
		return self.rawFunc

	def ReloadSetRawFunction(self, code):
		self.rawCodeObject = code

	def GetRawCodeObject(self):
		return self.rawCodeObject

	def ApplyWarp(self):
		# 原来是warp的用法
		# 那么 self.warpFunc 就是我们的MockCallFunc
		# f = self.rawFunc
		# localWarp = DebugLocalDecorator.DebugLocal
		# # 和 frame 有关
		# nf = localWarp(f, self.FunctionEventCall)
		# self.warpFunc = nf

		# 现在是reload用法
		# 那么 self.warpFunc 就是我们的newFunc
		f = self.rawFunc
		localWarp = DebugLocalDecorator.DebugNewFunc
		# 和 frame 有关
		nf = localWarp(f, self.FunctionEventCall)
		self.warpFunc = nf #

	def FunctionEventCall(self, event):
		# 发送事件到node 设置func
		event.debugFunc = self
		self.funcEvent(event)
