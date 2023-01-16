# -*- coding: utf-8 -*-
'''
:Author: huangzehua@corp.netease.com
:Create Date: 2021/12/29
:file: use for debug functions
'''

from Debug.MockDebug.MockConst import EventArgsObj
from ..StreamMeta import TriggerStream, SequenceStream
from Component.LogicEffectComponent.LogicEffectManager import LogicEffectManager

# 有个问题 如果手动的reloadHook的函数 这里没有reload 或许是reload 没有修改文件？？
# print(inspect.getsource(USpellCtrl.CheckSpellCost))
# 如果现在手动的在 CheckSpellCost 添加信息 这里的getsourc还是原来的文本
# 大概率是 inspect.getsourc 这个方法无法获取reload 后的东西 可能是没有替换的原因
# 所有后面可以自己实现这个方法 获取真正的函数


# 先临时写在这个文件夹
# FDDASDASDASD
# FFFFFLLLLYYYY

# 配置稍微有点复杂了 要写两个函数了
# 有没自动的AI能帮我写meta


class SpellCheckStream(SequenceStream):


	STREAM_TEXT = "施法check-S"

	SPELL_CONFIG = {
		"CombatCtrl": ["_DoPlayerUseSpell"],
		"USpellCtrl": ["CheckUseSpell", "CheckSpellCost", "CheckSpellInCoolDown"], # 注释掉一个这个 "CanUseSpellTargetCheck",
		"SpellDriver": ["SubjectiveUseSpell", "ObjectiveUseSpell", "UseSpell", "CheckSpellInCoolDown"],
		"USpellDriver": ["CommonCastSpell"],
	}

	def LoadStreamFunctions(self):
		streamList = []
		from Component.CombatUnitComponent.CombatCtrl import CombatCtrl
		from UComponent.CombatUnitComponent.USpellCtrl import USpellCtrl
		from UComponent.CombatUnitComponent.USpellDriver import USpellDriver
		from Component.CombatUnitComponent.SpellDriver import SpellDriver
		streamList.append((CombatCtrl, self.SPELL_CONFIG[CombatCtrl.__name__]))
		streamList.append((USpellCtrl, self.SPELL_CONFIG[USpellCtrl.__name__]))
		streamList.append((USpellDriver, self.SPELL_CONFIG[USpellDriver.__name__]))
		streamList.append((SpellDriver, self.SPELL_CONFIG[SpellDriver.__name__]))
		return streamList

	def GetFirstFunc(self):
		return ["CombatCtrl._DoPlayerUseSpell", "SpellDriver.SubjectiveUseSpell", "SpellDriver.ObjectiveUseSpell"]

	def SetFilterContext(self, event):
		lastFrame = event.lastFrame
		nodeFuncName = event.debugNode.node.__name__ + '.' + event.funcName
		filterContext = event.filterContext
		locals = lastFrame.f_locals
		localSelf = locals.get("self", None)
		funcs = self.GetFirstFunc()
		if nodeFuncName in funcs and localSelf:
			filterContext[EventArgsObj.Filter_Entity] = localSelf.entity.id # entity id
			filterContext[EventArgsObj.Filter_PrefabId] = localSelf.entity.prefabID # entity
			spellId = locals.get("spellId", None) or locals.get("spellID", None)
			print("dasda", spellId)
			filterContext[EventArgsObj.Filter_BehaviorId] = spellId # le的id
