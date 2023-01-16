# -*- coding: utf-8 -*

import collections

CALL_EVENTS_EXCEPTION_THRESHOLD = 3
__call_events__ = collections.Counter()


class Event(object):
	def __init__(self):
		self.registerFuncs = []

	def RegisterFunc(self, func):
		if func in self.registerFuncs:
			print("[WARNING]Event register one function twice!", func)
			return
		self.registerFuncs.append(func)

	def UnregisterFunc(self, func):
		try:
			self.registerFuncs.remove(func)
		except:
			pass

	def GetRegisterFunc(self):
		return self.registerFuncs

	def Destroy(self):
		self.registerFuncs = []

	def Activate(self, *args, **kwargs):
		if len(self.registerFuncs) == 0:
			return

		# 避免调用出现环
		if __call_events__[self] + 1 >= CALL_EVENTS_EXCEPTION_THRESHOLD:
			print(__call_events__)
			raise Exception("The stack of event call has a ring! Depth: %d" % CALL_EVENTS_EXCEPTION_THRESHOLD)

		__call_events__[self] += 1

		ret = None

		for f in self.registerFuncs:
			try:
				ret = f(*args, **kwargs)
			except:
				import traceback
				traceback.print_exc()

		__call_events__[self] -= 1
		return ret

	def __iadd__(self, func):
		self.RegisterFunc(func)
		return self

	def __isub__(self, func):
		self.UnregisterFunc(func)
		return self

	def __call__(self, *args, **kwargs):
		return self.Activate(*args, **kwargs)
