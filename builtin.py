# -*- coding: utf-8 -*-
"""skill2 内置技能：所有技能集中写在本文件。

新增技能只需在文件末尾继续添加 @skill 类，不用动 engine.py。
但 engine.py 必须在对应时机调用 s2_dispatch(self, who, "钩子名", ...)，否则不触发。

已接入的钩子（engine 对玩家+AI 都 dispatch）：
    on_prepare_phase(api)
    on_modify_draw_count(api) -> int
    on_end_phase(api)
    on_damaged(api, dmg, src, card, element)
    on_damage_dealt(api, target, dmg, card, element)
    on_judge_replace(api, card, why) -> card
    on_judge_after(api, card, why)
    on_equip_lost(api, card)
    on_sha_target(api, sha_card, target_who)
    on_be_sha_target(api, sha_card, from_who)
    on_duel_target(api, target_who)
    on_be_duel_target(api, from_who)
    on_enter_dying(api)
    on_card_to_discard(api, card, is_play, is_judge) -> bool
"""

from ..skill2 import skill


@skill("烈弓")
class Liegong:
    """烈弓：使用杀指定目标后，若目标手牌数大于你则不能出闪，若目标体力值大于你则伤害+1。"""
    def on_sha_target(self, api, sha_card, target_who):
        if api.who == target_who:
            return None
        target = api.state[target_who]
        my_hand = len(api.hand)
        my_hp = api.hp
        tgt_hand = len(target["hand"])
        tgt_hp = target["hp"]

        result = {"no_shan": False, "dmg_bonus": 0}
        if tgt_hand > my_hand:
            result["no_shan"] = True
            api.say(f"◆ 烈弓　目标手牌数({tgt_hand})>你({my_hand}),不能出闪")
        if tgt_hp > my_hp:
            result["dmg_bonus"] = 1
            api.say(f"◆ 烈弓　目标血量({tgt_hp})>你({my_hp}),伤害+1")
        if not result["no_shan"] and not result["dmg_bonus"]:
            return None
        return result


@skill("除疠")
class Chuli:
    """除疠：当你进入濒死状态时，摸一张牌。"""
    def on_enter_dying(self, api):
        got = api.draw(1)
        if got:
            api.say(f"◆ 除疠　进入濒死,摸1张({got[0]['s']}{got[0]['r']})")
        else:
            api.say("◆ 除疠　进入濒死,牌堆空")


@skill("激昂")
class Jiantang:
    """激昂：当你使用红色杀、被红色杀指定、使用决斗、被决斗指定时，各摸一张牌。"""
    def on_sha_target(self, api, sha_card, target_who):
        if sha_card["s"] not in ("♥", "♦"):
            return None
        got = api.draw(1)
        if got:
            api.say(f"◆ 激昂　使用红色杀,摸1张({got[0]['s']}{got[0]['r']})")
        return None

    def on_be_sha_target(self, api, sha_card, from_who):
        if sha_card["s"] not in ("♥", "♦"):
            return
        got = api.draw(1)
        if got:
            api.say(f"◆ 激昂　被红色杀指定,摸1张({got[0]['s']}{got[0]['r']})")

    def on_duel_target(self, api, target_who):
        got = api.draw(1)
        if got:
            api.say(f"◆ 激昂　使用决斗,摸1张({got[0]['s']}{got[0]['r']})")

    def on_be_duel_target(self, api, from_who):
        got = api.draw(1)
        if got:
            api.say(f"◆ 激昂　被决斗指定,摸1张({got[0]['s']}{got[0]['r']})")


@skill("魂姿")
class Hunzi:
    """魂姿：准备阶段若体力值为1，则失去1点体力上限，获得英姿和英魂。"""
    def on_prepare_phase(self, api):
        me = api.me
        if not me.get("hero"):
            return
        if me["hp"] != 1:
            return
        if me["maxhp"] <= 1:
            return
        hero = me["hero"]
        names = [s[0] for s in hero["s"]]
        if "英姿" in names and "英魂" in names:
            return
        me["maxhp"] -= 1
        if "英姿" not in names:
            hero["s"].append(("英姿", "摸牌阶段", "yingzi"))
        if "英魂" not in names:
            hero["s"].append(("英魂", "准备阶段", "yinghun"))
        api.say(f"◆ 魂姿　体力值为1,失去1点体力上限(现{me['maxhp']}),获得英姿、英魂")


@skill("独进")
class Dujin:
    """独进：摸牌阶段额外摸 1 + floor(装备数 / 2) 张牌。"""
    def on_modify_draw_count(self, api):
        equip_cnt = len(api.me.get("equip") or {})
        extra = 1 + equip_cnt // 2
        api.say(f"◆ 独进　装备数 {equip_cnt},额外摸 {extra} 张")
        return extra


@skill("落英")
class Luoying:
    """落英：回合外，梅花牌不因使用或打出进入弃牌堆时，获得之。"""
    def on_card_to_discard(self, api, card, is_play, is_judge):
        if card["s"] != "♣":
            return False
        if api.game.st["turn"] == api.who:
            return False
        api.me["hand"].append(card)
        api.say(f"◆ 落英　{'你' if api.who == 'you' else '我'}获得 {card['s']}{card['r']}{card['n']}")
        return True


@skill("酒诗")
class Jiushi:
    """酒诗（被动部分）：背面朝上受到伤害时翻面；翻回正面时摸一张牌。

    主动部分（正面朝上翻面视为酒）在 engine 的 _skill / _pending 濒死分支里处理。
    濒死状态下不触发被动翻面，避免无限自救。
    """
    def on_damaged(self, api, dmg, src, card, element):
        who = api.who
        if not api.game.st.get(f"flipped_{who}"):
            return
        if api.me["hp"] <= 0:
            return
        api.game.st[f"flipped_{who}"] = False
        api.say(f"◆ 酒诗　{'你' if who == 'you' else '我'}背面朝上受到伤害，翻回正面")
        got = api.draw(1)
        if got:
            api.say(f"◆ 酒诗　翻回正面，摸1张({got[0]['s']}{got[0]['r']})")


@skill("成章")
class Chengzhang:
    """成章：受到伤害获得章标记，7个章时清除并回复1点体力摸2张。"""
    def on_damaged(self, api, dmg, src, card, element):
        me = api.me
        me["zhang"] = me.get("zhang", 0) + 1
        api.say(f"◆ 成章　获得1个章标记（当前{me['zhang']}/7）")
        if me["zhang"] >= 7:
            me["zhang"] = 0
            api.say("◆ 成章　七个章标记已满，清除并回复1点体力，摸2张")
            if me["hp"] < me["maxhp"]:
                api.heal(1)
            api.draw(2)