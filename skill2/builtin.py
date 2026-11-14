# -*- coding: utf-8 -*-
"""skill2 内置技能：所有技能集中写在本文件。"""

import re as _re
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
    """酒诗（被动部分）：背面朝上受到伤害时翻面；翻回正面时摸一张牌。主动部分在 engine 内。"""
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


@skill("执义")
class Zhiyi:
    """执义：每回合限一次，当你本回合使用过基本牌后，当前回合角色的回合结束时，你可以将一张手牌当做一张无次数限制的基本牌使用或打出。"""

    def on_turn_start(self, api):
        api.me["_zhiyi_basic"] = False
        api.me["_zhiyi_used"] = False

    def on_use_basic(self, api, card):
        n = card.get("n") if card else None
        if n in ("杀", "火杀", "雷杀", "桃", "酒", "闪"):
            api.me["_zhiyi_basic"] = True

    def on_end_phase(self, api):
        from ..engine import has, armor, wep, other
        st = api.state
        me = api.me
        if not me.get("_zhiyi_basic"):
            return None
        if me.get("_zhiyi_used"):
            return None
        if not api.hand:
            return None
        me["_zhiyi_used"] = True
        
        current_turn = st.get("turn", "you")
        next_who = other(current_turn)
        
        if api.who == "you":
            st["pending"] = {
                "t": "zhiyi_opt",
                "next_turn": next_who,
                "who": "you",
            }
            api.say("◆ 执义　本回合使用过基本牌,可发动:回 牌序号+空格+类型(s=杀,t=桃,j=酒,f=火杀,l=雷杀),如 1 s,0=不发动")
            return True
        elif api.game.is_pvp:
            st["pending"] = {
                "t": "zhiyi_opt",
                "next_turn": next_who,
                "who": api.who,
            }
            api.say("◆ 执义　本回合使用过基本牌,可发动:回 牌序号+空格+类型(s=杀,t=桃,j=酒,f=火杀,l=雷杀),如 1 s,0=不发动")
            return True
        else:
            self._ai_execute(api, next_who)
            return True

    def on_pending(self, api, pending, text):
        import re as _re
        from ..engine import has, wep, armor, distance, attack_range, elem_of
        if pending.get("t") != "zhiyi_opt":
            return None
        st = api.state
        you = api.me
        me = st["me"]
        st["pending"] = None
        raw = (text or "").strip().lower()
        if raw in ("0", "", "过", "不发动", "取消"):
            api.say("◆ 执义　不发动")
            api.game._turn(pending["next_turn"])
            return True
        
        m = _re.match(r"^(\d+)\s*([stjfl]?)$", raw.replace(" ", ""))
        if not m:
            api.say("◆ 提示　回 牌序号+空格+类型(s=杀,t=桃,j=酒,f=火杀,l=雷杀),如 1 s,0=不发动")
            you["_zhiyi_used"] = False
            st["pending"] = pending
            return True
            
        idx = int(m.group(1))
        typ = m.group(2) or "s"
        if not (1 <= idx <= len(you["hand"])):
            api.say("◆ 提示　没这张牌")
            you["_zhiyi_used"] = False
            st["pending"] = pending
            return True
            
        c = you["hand"][idx - 1]
        
        if typ == "t" and you["hp"] >= you["maxhp"]:
            api.say("◆ 提示　满血,桃无效,请重新选择或0=不发动")
            you["_zhiyi_used"] = False
            st["pending"] = pending
            return True
            
        if typ in ("s", "f", "l"):
            if has(me, "空城") and not me["hand"]:
                api.say("◆ 提示　对方空城,不能杀")
                you["_zhiyi_used"] = False
                st["pending"] = pending
                return True
            if distance(you, me) - st.get("distance_bonus", 0) > attack_range(you):
                api.say(f"◆ 提示　距离 {distance(you, me)} > 攻击范围 {attack_range(you)},杀不到")
                you["_zhiyi_used"] = False
                st["pending"] = pending
                return True
                
        you["hand"] = [x for x in you["hand"] if x["i"] != c["i"]]
        st["discard"].append(c)
        
        if typ in ("s", "f", "l"):
            card_n = {"s": "杀", "f": "火杀", "l": "雷杀"}[typ]
            virtual = {"i": c["i"], "s": c["s"], "r": c["r"], "n": card_n}
            api.say(f"◆ 执义　{c['s']}{c['r']}{c['n']} 当 {card_n} 使用(无视次数)")
            self._player_sha(api, virtual)
            if st.get("pending"):
                st["_zhiyi_after_turn"] = pending["next_turn"]
                return True
        elif typ == "t":
            you["hp"] += 1
            api.say(f"◆ 执义　{c['s']}{c['r']}{c['n']} 当桃,回复1点,回到 {you['hp']}")
        elif typ == "j":
            st["jiu"] = True
            api.say("◆ 执义　当酒使用")
            
        api.game._turn(pending["next_turn"])
        return True

    def _player_sha(self, api, card):
        from ..engine import has, wep, armor, elem_of
        st = api.state
        you = api.me
        me = st["me"]
        if has(me, "空城") and not me["hand"]:
            api.say("◆ 空城　对方无手牌,杀无效")
            return
        is_black = card["s"] in ("♠", "♣")
        is_attr = card["n"] in ("火杀", "雷杀")
        has_qg = wep(you) == "青釭剑"
        if armor(me) == "仁王盾" and is_black and not has_qg:
            api.say("◆ 仁王盾　黑杀无效")
            return
        if armor(me) == "藤甲" and not has_qg and not is_attr:
            api.say("◆ 藤甲　普通杀无效")
            return
        if api.game._ai_shan(1, ignore_armor=has_qg):
            api.say("◆ 结算　我出闪,杀没中")
            return
        api.game.hurt("me", 1, "you", card=card, element=elem_of(card))

    def _ai_execute(self, api, next_who):
        from ..engine import has, wep, armor, elem_of, distance, attack_range
        st = api.state
        me = api.me
        you = st["you"]

        if me["hp"] < me["maxhp"]:
            tao = next((c for c in me["hand"] if c["n"] == "桃"), None)
            if tao:
                me["hand"] = [x for x in me["hand"] if x["i"] != tao["i"]]
                st["discard"].append(tao)
                me["hp"] += 1
                api.say(f"◆ 执义　我用 {tao['s']}{tao['r']}{tao['n']} 桃回复1点,回到 {me['hp']}")
                api.game._check_jieyin()
                api.game._turn(next_who)
                return

        if you["hand"] and not has(you, "空城") and distance(me, you) <= attack_range(me):
            worst = sorted(me["hand"], key=lambda x: 0 if x["n"] not in ("桃", "无懈可击", "杀", "闪") else 1)[0]
            me["hand"] = [x for x in me["hand"] if x["i"] != worst["i"]]
            st["discard"].append(worst)
            virtual = {"i": worst["i"], "s": worst["s"], "r": worst["r"], "n": "杀"}
            
            is_black = worst["s"] in ("♠", "♣")
            has_qg = wep(me) == "青釭剑"
            
            if armor(you) == "仁王盾" and is_black and not has_qg:
                api.say(f"◆ 执义　我把 {worst['s']}{worst['r']}{worst['n']} 当杀使用,但被仁王盾抵消")
                api.game._turn(next_who)
                return
            if armor(you) == "藤甲" and not has_qg:
                api.say(f"◆ 执义　我把 {worst['s']}{worst['r']}{worst['n']} 当杀使用,但被藤甲抵消")
                api.game._turn(next_who)
                return
                
            api.say(f"◆ 执义　我发动,将 {worst['s']}{worst['r']}{worst['n']} 当【杀】对你使用(无视次数)")
            
            st["_zhiyi_after_turn"] = next_who
            
            st["pending"] = {
                "t": "shan",
                "times": 1,
                "dmg": 1,
                "qb": armor(you) == "八卦阵" and not has_qg,
                "src": "me",
                "card": virtual,
                "element": None,
                "no_shan": False,
                "who": "you",
            }
            return

        api.say("◆ 执义　我放弃发动")
        api.game._turn(next_who)


@skill("志继")
class Zhiji:
    """志继：觉醒技，准备阶段，若你没有手牌，选择一项：回复1点体力或摸两张牌，然后获得观星。"""
    def on_prepare_phase(self, api):
        me = api.me
        if not me.get("hero"):
            return
        if me.get("zhiji_awakened"):
            return
        if me["hand"]:
            return
            
        me["zhiji_awakened"] = True
        
        names = [s[0] for s in me["hero"]["s"]]
        if "观星" not in names:
            me["hero"]["s"].append(("观星", "准备阶段", "guanxing"))
            api.say("◆ 志继　觉醒：获得技能【观星】")
        
        if api.who == "you":
            st = api.state
            st["pending"] = {"t": "zhiji_opt", "who": "you"}
            api.say("◆ 志继　觉醒技：你没有手牌。1=回复1点体力 2=摸两张牌")
            return True
        elif api.game.is_pvp:
            st = api.state
            st["pending"] = {"t": "zhiji_opt", "who": api.who}
            api.say("◆ 志继　觉醒技：你没有手牌。1=回复1点体力 2=摸两张牌")
            return True
        else:
            if me["hp"] < me["maxhp"]:
                me["hp"] += 1
                api.say("◆ 志继　我选择回复1点体力")
            else:
                api.game.draw(api.who, 2)
                api.say("◆ 志继　我选择摸两张牌")

    def on_pending(self, api, pending, text):
        from ..engine import has
        if pending.get("t") != "zhiji_opt":
            return None
        st = api.state
        you = st["you"]
        st["pending"] = None
        if text == "1":
            you["hp"] = min(you["hp"] + 1, you["maxhp"])
            api.say(f"◆ 志继　回复1点体力,回到 {you['hp']}")
        elif text == "2":
            api.game.draw("you", 2)
            api.say("◆ 志继　摸两张牌")
        else:
            api.say("◆ 提示　1=回复1点体力 2=摸两张牌")
            st["pending"] = pending
            return True
        
        if has(you, "观星"):
            top = [api.game.deck.pop() for _ in range(min(3, len(api.game.deck)))] if api.game.deck else []
            if top:
                st["pending"] = {"t": "guanxing", "cards": top, "who": "you"}
                api.say("◆ 观星　牌堆顶:" + "　".join(f"{i}={c['s']}{c['r']}{c['n']}" for i, c in enumerate(top, 1)) + "　回「顶1 2 3」或「顶1 底2 3」或「底1 2 3」")
                return True
        api.game._judge_next()
        return True


@skill("挑衅")
class Tiaoxin:
    """挑衅：出牌阶段限一次，你可以令一名角色对你使用一张杀，否则你弃置其区域内一张牌。"""
    def on_turn_start(self, api):
        api.me["tiaoxin_used"] = False

    def on_skill(self, api, key):
        if key != "tiaoxin":
            return None
        from ..engine import has, distance, attack_range
        st = api.state
        you = api.me
        me = st["me"]
        
        if api.me.get("tiaoxin_used"):
            api.say("◆ 提示　挑衅本回合已用过")
            return True
        if not api.game._all_cards("me"):
            api.say("◆ 提示　对方没有牌可以弃置")
            return True
            
        api.me["tiaoxin_used"] = True
        api.say("◆ 挑衅　你发动挑衅，令对手对你使用一张杀，否则弃置其一张牌")
        can_hit = distance(me, you) <= attack_range(me)
        if api.game.is_pvp:
            st["pending"] = {"t": "tiaoxin_sha", "can_hit": can_hit, "who": "me"}
            api.say("◆ 挑衅　对方请选择是否对挑衅者使用一张杀(回序号),否则被弃置一张牌,0=不出杀")
            return True
        
        sha_c, sha_desc = api.game._ai_find_sha()
        if sha_c and can_hit:
            api.game._hand_out("me", sha_c)
            st["discard"].append(sha_c)
            api.say(f"◆ 挑衅　对手出 {sha_c['s']}{sha_c['r']}{sha_c['n']} 作为杀")
            api.game._ai_sha_attack(sha_c)
        else:
            if not can_hit:
                api.say("◆ 挑衅　对方无法使用杀攻击你，被你弃置一张牌")
            else:
                api.say("◆ 挑衅　对方无法使用杀响应，被你弃置一张牌")
            opts = api.game._build_pick_opts("me")
            if opts:
                st["pending"] = {"t": "pick_card", "kind": "tiaoxin", "src": "me", "who": "you"}
                line = "　".join(f"{num}={lab}" for num, _, _, lab in opts)
                api.say(f"◆ 挑衅　选择弃置对方一张: {line} (回显示的编号)")
        return True

    def on_ai_action(self, api):
        from ..engine import has, distance, attack_range
        st = api.state
        me = api.me
        you = st["you"]
        if api.me.get("tiaoxin_used"):
            return None
        if not api.game._all_cards("you"):
            return None
            
        api.me["tiaoxin_used"] = True
        api.say("◆ 挑衅　我发动挑衅，令你对我使用一张杀，否则我弃置你一张牌")
        can_hit = distance(you, me) - st.get("distance_bonus", 0) <= attack_range(you)
        st["pending"] = {"t": "tiaoxin_sha", "can_hit": can_hit, "who": "you"}
        return True

    def on_pending(self, api, pending, text):
        from ..engine import has
        if pending.get("t") != "tiaoxin_sha":
            return None
        st = api.state
        you = st["you"]
        me = st["me"]
        if text in ("0", "过", "不出", "不杀"):
            st["pending"] = None
            api.say("◆ 挑衅　你未使用杀，被弃置一张牌")
            tgt = api.game._pick_card("you", allow_judge=False)
            if tgt:
                api.game._discard("you", tgt, allow_pending=False)
                api.say(f"◆ 挑衅　我弃置你 {tgt['s']}{tgt['r']}{tgt['n']}")
            api.game._resume_ai_if_needed()
            return True
        
        c = api.game._hand(int(text)) if text.isdigit() else None
        ok = c and (c["n"] in ("杀", "火杀", "雷杀") or (has(you, "龙胆") and c["n"] == "闪") or (has(you, "武圣") and c["s"] in ("♥", "♦")))
        if not ok:
            api.say("◆ 提示　回杀序号或0=不出杀")
            return True
        
        if not pending.get("can_hit"):
            api.say("◆ 挑衅　你的攻击范围不够，无法出杀，将被弃置一张牌")
            tgt = api.game._pick_card("you", allow_judge=False)
            if tgt:
                api.game._discard("you", tgt, allow_pending=False)
                api.say(f"◆ 挑衅　我弃置你 {tgt['s']}{tgt['r']}{tgt['n']}")
            api.game._resume_ai_if_needed()
            return True
        
        api.game._discard("you", c, is_play=True)
        api.say(f"◆ 挑衅　你出 {c['s']}{c['r']}{c['n']} 当杀")
        virtual = c if c["n"] in ("杀", "火杀", "雷杀") else {"i": c["i"], "s": c["s"], "r": c["r"], "n": "杀"}
        st["pending"] = None
        api.game._resolve_sha(virtual)
        if not st["over"] and not st.get("pending") and st["turn"] == "me":
            api.game._ai_play()
        return True


@skill("天义")
class Tianyi:
    """天义：出牌阶段限一次，摸一张牌并拼点。赢则无距离次数限制，输则不能出杀。"""
    def on_turn_start(self, api):
        api.me["tianyi_used"] = False
        api.me["tianyi_win"] = False
        api.me["tianyi_lose"] = False

    def on_modify_sha_limit(self, api, base_limit):
        if api.me.get("tianyi_win"):
            return 99
        if api.me.get("tianyi_lose"):
            return 0
        return base_limit

    def on_modify_distance(self, api, dist, dst_who):
        if api.me.get("tianyi_win"):
            return 0
        return dist

    def on_skill(self, api, key):
        if key != "tianyi":
            return None
        st = api.state
        you = api.me
        me = st["me"]
        if you.get("tianyi_used"):
            api.say("◆ 提示　天义本回合已用过")
            return True
        if not you["hand"] or not me["hand"]:
            api.say("◆ 提示　双方必须有手牌才能拼点")
            return True
        you["tianyi_used"] = True
        api.draw(1)
        api.say("◆ 天义　你摸1张牌,请选择一张手牌进行拼点(回序号)")
        st["pending"] = {"t": "tianyi_pick", "who": "you"}
        return True

    def on_ai_action(self, api):
        st = api.state
        me = api.me
        you = st["you"]
        from ..engine import RANKS
        if me.get("tianyi_used"):
            return None
        if not me["hand"] or not you["hand"]:
            return None
        me["tianyi_used"] = True
        api.draw(1)
        api.say("◆ 天义　我发动天义,摸1张并拼点")
        me_card = sorted(me["hand"], key=lambda x: RANKS.index(x["r"]), reverse=True)[0]
        api.game._hand_out("me", me_card)
        st["discard"].append(me_card)
        
        if api.game.is_pvp:
            st["pending"] = {"t": "tianyi_respond", "ai_card": me_card, "who": "you", "caster": "me"}
            api.say("◆ 天义　我已扣置一张手牌，请你选择一张手牌拼点(回序号)")
            return True
            
        st["pending"] = {"t": "tianyi_respond", "ai_card": me_card, "who": "you", "caster": "me"}
        api.say("◆ 天义　我已将一张手牌扣置作为拼点牌，请出一张手牌拼点(回序号)")
        return True

    def on_pending(self, api, pending, text):
        t = pending.get("t")
        if t not in ("tianyi_pick", "tianyi_respond"):
            return None

        st = api.state
        you = st["you"]
        me = st["me"]

        from ..engine import RANKS
        def _pt(x): return RANKS.index(x["r"])

        if t == "tianyi_pick":
            if text == "0":
                api.say("◆ 提示　必须选一张牌拼点,回序号")
                return True
            c = api.game._hand(int(text)) if text.isdigit() else None
            if not c:
                api.say("◆ 提示　回正确的手牌序号")
                return True

            you["hand"] = [x for x in you["hand"] if x["i"] != c["i"]]
            st["discard"].append(c)

            if not me["hand"]:
                api.say(f"◆ 天义　你拼点 {c['s']}{c['r']}{c['n']},对方无手牌,自动获胜")
                self._settle(api, True, "you")
                st["pending"] = None
                return True

            if api.game.is_pvp:
                st["pending"] = {"t": "tianyi_respond", "ai_card": c, "who": "me", "caster": "you"}
                api.say("◆ 天义　你已扣置了一张手牌，对方请选择一张手牌拼点(回序号)")
                return True

            me_card = sorted(me["hand"], key=_pt, reverse=True)[0]
            me["hand"] = [x for x in me["hand"] if x["i"] != me_card["i"]]
            st["discard"].append(me_card)

            api.say(f"◆ 天义　双方同时亮出：你 {c['s']}{c['r']}{c['n']} vs 对手 {me_card['s']}{me_card['r']}{me_card['n']}")
            win = _pt(c) > _pt(me_card)
            self._settle(api, win, "you")
            st["pending"] = None
            return True

        elif t == "tianyi_respond":
            c = api.game._hand(int(text)) if text.isdigit() else None
            if not c:
                api.say("◆ 提示　回正确的手牌序号")
                return True

            api.me["hand"] = [x for x in api.me["hand"] if x["i"] != c["i"]]
            st["discard"].append(c)

            me_card = pending["ai_card"]
            caster = pending.get("caster", "me")
            
            c1 = me_card if caster == "you" else c
            c2 = c if caster == "you" else me_card
            
            api.say(f"◆ 天义　双方同时亮出：{c1['s']}{c1['r']}{c1['n']} vs {c2['s']}{c2['r']}{c2['n']}")
            win = _pt(c1) > _pt(c2)
            self._settle(api, win, caster)
            
            st["pending"] = None
            if not st["over"] and st["turn"] == "me":
                api.game._resume_ai_if_needed()
            return True

        return None

    def _settle(self, api, win, caster):
        st = api.state
        target = st[caster]
        if win:
            api.say(f"◆ 天义　{'你' if caster == 'you' else '我'}赢了!本回合使用牌无次数无距离限制")
            target["tianyi_win"] = True
            target["tianyi_lose"] = False
        else:
            api.say(f"◆ 天义　{'你' if caster == 'you' else '我'}输了,本回合不能使用杀")
            target["tianyi_win"] = False
            target["tianyi_lose"] = True


@skill("行殇")
class Xingshang:
    """行殇：自身造成伤害时获得殇标记；出牌阶段限一次，弃置1/2/3个殇令目标本回合禁用装备/锦囊/基本牌。"""
    def on_any_damaged(self, api, victim_who, dmg, src, card, element):
        if src != api.who:
            return
        me = api.me
        me["shang"] = me.get("shang", 0) + dmg
        api.say(f"◆ 行殇　你造成了伤害,获得{dmg}个殇标记(当前{me['shang']}个)")

    def on_skill(self, api, key):
        if key != "xingshang":
            return None
        me = api.me
        if me.get("shang", 0) < 1:
            api.say("◆ 提示　没有殇标记")
            return True
        st = api.state
        if st.get("ban_me_basic") and st.get("ban_me_trick") and st.get("ban_me_equip"):
            api.say("◆ 提示　对方已经被完全限制")
            return True
        st["pending"] = {"t": "xingshang_opt", "who": "you"}
        api.say(f"◆ 行殇　当前拥有 {me['shang']} 个殇标记，请选择弃置数量：1=禁用装备 2=禁用锦囊 3=禁用基本牌，0=取消")
        return True

    def on_pending(self, api, pending, text):
        if pending.get("t") != "xingshang_opt":
            return None
        me = api.me
        st = api.state
        if text in ("0", "取消"):
            api.say("◆ 行殇　取消发动")
            st["pending"] = None
            return True
        
        cost = int(text) if text in ("1", "2", "3") else 0
        if cost == 0 or me.get("shang", 0) < cost:
            api.say("◆ 提示　标记不足或输入错误，请重新选择")
            return True
            
        if cost == 1 and st.get("ban_me_equip"):
            api.say("◆ 提示　对方已被禁用装备牌")
            return True
        if cost == 2 and st.get("ban_me_trick"):
            api.say("◆ 提示　对方已被禁用锦囊牌")
            return True
        if cost == 3 and st.get("ban_me_basic"):
            api.say("◆ 提示　对方已被禁用基本牌")
            return True
            
        me["shang"] -= cost
        ban_type = "equip" if cost == 1 else ("trick" if cost == 2 else "basic")
        type_name = "装备牌" if cost == 1 else ("锦囊牌" if cost == 2 else "基本牌")
        
        api.say(f"◆ 行殇　你弃置 {cost} 个标记，令对手本回合不能使用【{type_name}】")
        st[f"ban_me_{ban_type}"] = True
        st["pending"] = None
        return True

    def on_ai_action(self, api):
        st = api.state
        me = api.me
        you = st["you"]
        if me.get("shang", 0) < 1:
            return None
        if st.get("ban_you_basic") and st.get("ban_you_trick") and st.get("ban_you_equip"):
            return None
            
        if me["shang"] >= 3 and len(you["hand"]) >= 3 and not st.get("ban_you_basic"):
            cost = 3
        elif me["shang"] >= 2 and not st.get("ban_you_trick"):
            cost = 2
        elif not st.get("ban_you_equip"):
            cost = 1
        else:
            return None
            
        me["shang"] -= cost
        ban_type = "equip" if cost == 1 else ("trick" if cost == 2 else "basic")
        type_name = "装备牌" if cost == 1 else ("锦囊牌" if cost == 2 else "基本牌")
        
        api.say(f"◆ 行殇　我弃置 {cost} 个殇标记，令你本回合不能使用【{type_name}】")
        st[f"ban_you_{ban_type}"] = True
        return None


@skill("放逐")
class Fangzhu:
    """放逐：受到1点伤害后，令一名角色翻面并摸X张牌（X为已失去体力）。"""
    def on_damaged(self, api, dmg, src, card, element):
        me = api.me
        lost_hp = me["maxhp"] - me["hp"]
        if lost_hp <= 0:
            return

        if api.who == "you":
            st = api.state
            st["pending"] = {"t": "fangzhu_opt", "lost_hp": lost_hp, "who": api.who}
            if me["hp"] > 0:
                api.say(f"◆ 放逐　你受到伤害，可以令对手翻面并摸{lost_hp}张牌。1=放逐敌人 0=取消")
            return True
        elif api.game.is_pvp:
            st = api.state
            st["pending"] = {"t": "fangzhu_opt", "lost_hp": lost_hp, "who": api.who}
            if me["hp"] > 0:
                api.say(f"◆ 放逐　你可以令对手翻面并摸{lost_hp}张牌。1=放逐敌人 0=取消")
            return True
        else:
            st = api.state
            you_flipped = st.get("flipped_you", False)

            if not you_flipped:
                st["flipped_you"] = True
                api.say(f"◆ 放逐　我发动放逐，令你翻面并摸{lost_hp}张牌")
                api.game.draw("you", lost_hp)
            else:
                api.say("◆ 放逐　你已翻面，放弃发动")
            return None

    def on_pending(self, api, pending, text):
        if pending.get("t") != "fangzhu_opt":
            return None
        st = api.state
        lost_hp = pending["lost_hp"]
        if text in ("0", "取消"):
            api.say("◆ 放逐　取消发动")
            st["pending"] = None
            if api.game._pop_pending_after():
                return True
            if not st["over"] and st["turn"] == "me":
                api.game._resume_ai_if_needed()
            return True

        if text == "1":
            st["pending"] = None
            if pending.get("who") == "you":
                st["flipped_me"] = True
                api.say(f"◆ 放逐　你令对手翻面并摸{lost_hp}张牌")
                api.game.draw("me", lost_hp)
            else:
                st["flipped_you"] = True
                api.say(f"◆ 放逐　我发动放逐，令你翻面并摸{lost_hp}张牌")
                api.game.draw("you", lost_hp)
            if api.game._pop_pending_after():
                return True
            if not st["over"] and st["turn"] == "me":
                api.game._resume_ai_if_needed()
            return True

        api.say("◆ 提示　请输入 1=放逐敌人 0=取消")
        return True


@skill("趫猛")
class Qiaomeng:
    """趫猛：当你使用杀造成伤害后，你可以获得其装备区里的一张牌。"""
    def on_damage_dealt(self, api, target_who, dmg, card, element):
        if not card or card.get("n") not in ("杀", "火杀", "雷杀"):
            return
        target = api.state[target_who]
        if not target["equip"]:
            return

        import random
        slot = random.choice(list(target["equip"].keys()))
        eq_card = target["equip"][slot]
        api.game._steal(target_who, eq_card, api.who)
        tgt_name = "你" if target_who == "you" else "对手"
        api.say(f"◆ 趫猛　获得{tgt_name}的装备 {eq_card['s']}{eq_card['r']}{eq_card['n']}")


@skill("义从")
class Yicong:
    """义从：锁定技，若你的体力值大于2，你计算与其他角色的距离-1；若你的体力值小于等于2，其他角色计算与你的距离+1。"""
    pass


@skill("克己")
class Keji:
    """克己：出牌阶段若你未使用杀则你可以跳过弃牌阶段。"""
    pass


@skill("勤学")
class Qinxue:
    """勤学：觉醒技，准备阶段，若你的手牌数大于你的体力值+3，你摸两张牌并获得'攻心'，且本回合使用杀无次数限制。"""
    def on_prepare_phase(self, api):
        me = api.me
        if me.get("qinxue_awakened"):
            return
        if len(me["hand"]) > me["hp"] + 3:
            me["qinxue_awakened"] = True
            api.say("◆ 勤学　觉醒：手牌数大于体力值+3，摸两张牌并获得【攻心】，本回合使用杀无次数限制")
            api.draw(2)
            names = [s[0] for s in me["hero"]["s"]]
            if "攻心" not in names:
                me["hero"]["s"].append(("攻心", "出牌阶段限一次", "gongxin"))
            api.state["sha_limit_bonus"] = 99


@skill("攻心")
class Gongxin:
    """攻心：出牌阶段限一次，你可以观看一名角色的手牌，然后弃置其中一张红桃牌。"""
    def on_turn_start(self, api):
        api.me["gongxin_used"] = False

    def on_skill(self, api, key):
        if key != "gongxin":
            return None
        me = api.me
        if me.get("gongxin_used"):
            api.say("◆ 提示　攻心本回合已用过")
            return True

        target_who = "me" if api.who == "you" else "you"
        other = api.state[target_who]

        me["gongxin_used"] = True
        if not other["hand"]:
            api.say("◆ 攻心　对方没有手牌，无法发动")
            return True

        opts_list = [(i, c) for i, c in enumerate(other["hand"], 1) if c["s"] == "♥"]
        opts_line = "　".join(f"{i}={c['s']}{c['r']}{c['n']}" for i, c in opts_list)

        api.say(f"◆ 攻心　观看对方手牌：" + " ".join(f"[{c['s']}{c['r']} {c['n']}]" for c in other["hand"]))

        if not opts_list:
            api.say("◆ 攻心　对方没有红桃牌，无法弃置")
            return True

        api.state["pending"] = {"t": "gongxin_pick", "opts_line": opts_line, "who": "you"}
        api.say(f"◆ 攻心　选择弃置一张红桃牌：{opts_line} (回显示的编号)，0=不弃置")
        return True

    def on_pending(self, api, pending, text):
        if pending.get("t") != "gongxin_pick":
            return None

        st = api.state
        target_who = "me" if api.who == "you" else "you"
        other = st[target_who]

        if text in ("0", "过", "取消"):
            api.say("◆ 攻心　不弃置红桃牌")
            st["pending"] = None
            return True

        idx = int(text) if text.isdigit() else -1
        if 1 <= idx <= len(other["hand"]):
            c = other["hand"][idx - 1]
            if c["s"] == "♥":
                api.game._discard(target_who, c)
                api.say(f"◆ 攻心　弃置对方 {c['s']}{c['r']}{c['n']}")
                st["pending"] = None
                return True
        
        api.say("◆ 提示　请选择一张红桃牌，或0=取消")
        return True

    def on_ai_action(self, api):
        me = api.me
        if me.get("gongxin_used"):
            return None
        target_who = "me" if api.who == "you" else "you"
        other = api.state[target_who]
        if not other["hand"]:
            return None

        hearts = [(i, c) for i, c in enumerate(other["hand"], 1) if c["s"] == "♥"]
        if not hearts:
            return None

        me["gongxin_used"] = True
        idx, c = hearts[0]
        api.game._discard(target_who, c)
        api.say(f"◆ 攻心　我观看你手牌，弃置红桃 {c['s']}{c['r']}{c['n']}")
        return None


@skill("神速")
class Shensu:
    """神速：跳过摸牌阶段并使用一张杀；跳过出牌阶段并弃置一张装备牌使用一张杀；跳过弃牌阶段并翻面使用一张杀。以上杀均无视距离。"""

    def on_turn_start(self, api):
        api.me["shensu_used_1"] = False
        api.me["shensu_used_2"] = False
        api.me["shensu_used_3"] = False

    def on_draw_phase_start(self, api):
        me = api.me
        if me.get("shensu_used_1"):
            return None
        if api.who == "you":
            st = api.state
            st["pending"] = {"t": "shensu_opt", "phase": 1, "who": "you"}
            api.say("◆ 神速　你可以跳过摸牌阶段，并视为使用一张无视距离的【杀】。1=发动 0=取消")
            return True
        elif api.game.is_pvp:
            st = api.state
            st["pending"] = {"t": "shensu_opt", "phase": 1, "who": api.who}
            api.say("◆ 神速　你可以跳过摸牌阶段，并视为使用一张无视距离的【杀】。1=发动 0=取消")
            return True
        else:
            me["shensu_used_1"] = True
            api.state["jp"]["skip_draw"] = True
            api.say("◆ 神速　我跳过摸牌阶段，视为使用【杀】")
            virtual = {"n": "杀", "s": "", "r": "", "i": -1}
            api.game._ai_sha_attack(virtual)
            if not api.state.get("pending") and not api.state["over"]:
                api.game._after_draw("me", api.state["jp"]["skip_play"])
            else:
                api.state["_shensu_after"] = "draw"
            return True

    def on_play_phase_start(self, api):
        from ..engine import WEAPONS, ARMORS
        me = api.me
        if me.get("shensu_used_2"):
            return None
        equip_cards = [c for c in me["hand"] if c["n"] in WEAPONS or c["n"] in ARMORS or c["n"] in ("-1马", "+1马")]
        if not equip_cards:
            return None
        if api.who == "you":
            st = api.state
            st["pending"] = {"t": "shensu_opt", "phase": 2, "who": "you"}
            api.say("◆ 神速　你可以跳过出牌阶段并弃置一张装备牌，视为使用一张无视距离的【杀】。1=发动 0=取消")
            return True
        elif api.game.is_pvp:
            st = api.state
            st["pending"] = {"t": "shensu_opt", "phase": 2, "who": api.who}
            api.say("◆ 神速　你可以跳过出牌阶段并弃置一张装备牌，视为使用一张无视距离的【杀】。1=发动 0=取消")
            return True
        else:
            me["shensu_used_2"] = True
            api.state["jp"]["skip_play"] = True
            import random
            eq = random.choice(equip_cards)
            me["hand"] = [x for x in me["hand"] if x["i"] != eq["i"]]
            api.state["discard"].append(eq)
            api.say(f"◆ 神速　我跳过出牌阶段，弃置装备 {eq['s']}{eq['r']}{eq['n']}，视为使用【杀】")
            virtual = {"n": "杀", "s": "", "r": "", "i": -1}
            api.game._ai_sha_attack(virtual)
            if not api.state.get("pending") and not api.state["over"]:
                api.game._end("me")
            else:
                api.state["_shensu_after"] = "play"
            return True

    def on_discard_phase_start(self, api):
        me = api.me
        if me.get("shensu_used_3"):
            return None
        if api.state.get("flipped_" + api.who):
            return None
        if api.who == "you":
            st = api.state
            st["pending"] = {"t": "shensu_opt", "phase": 3, "who": "you"}
            api.say("◆ 神速　你可以跳过弃牌阶段并翻面，视为使用一张无视距离的【杀】。1=发动 0=取消")
            return True
        elif api.game.is_pvp:
            st = api.state
            st["pending"] = {"t": "shensu_opt", "phase": 3, "who": api.who}
            api.say("◆ 神速　你可以跳过弃牌阶段并翻面，视为使用一张无视距离的【杀】。1=发动 0=取消")
            return True
        else:
            me["shensu_used_3"] = True
            api.state["flipped_me"] = True
            api.say("◆ 神速　我跳过弃牌阶段，翻面，视为使用【杀】")
            virtual = {"n": "杀", "s": "", "r": "", "i": -1}
            api.game._ai_sha_attack(virtual)
            if not api.state.get("pending") and not api.state["over"]:
                api.game._end_phase("me")
            else:
                api.state["_shensu_after"] = "discard"
            return True

    def on_pending(self, api, pending, text):
        from ..engine import WEAPONS, ARMORS
        t = pending.get("t")
        if t not in ("shensu_opt", "shensu_pick"):
            return None
        st = api.state
        me = api.me
        if t == "shensu_opt":
            phase = pending["phase"]
            if text in ("0", "过", "取消"):
                api.say("◆ 神速　取消发动")
                st["pending"] = None
                if phase == 1:
                    api.game._normal_draw("you")
                    api.game._after_draw("you", st["jp"]["skip_play"])
                elif phase == 2:
                    pass
                elif phase == 3:
                    api.game._end("you")
                return True
            if text == "1":
                st["pending"] = None
                if phase == 1:
                    me["shensu_used_1"] = True
                    st["jp"]["skip_draw"] = True
                    api.say("◆ 神速　你跳过摸牌阶段，视为使用【杀】")
                    virtual = {"n": "杀", "s": "", "r": "", "i": -1}
                    api.game._resolve_sha(virtual)
                    if not st.get("pending") and not st["over"]:
                        api.game._after_draw("you", st["jp"]["skip_play"])
                    else:
                        st["_shensu_after"] = "draw"
                    return True
                elif phase == 2:
                    st["pending"] = {"t": "shensu_pick", "who": "you"}
                    equips = [c for c in me["hand"] if c["n"] in WEAPONS or c["n"] in ARMORS or c["n"] in ("-1马", "+1马")]
                    parts = [f"{i}={c['s']}{c['r']}{c['n']}" for i, c in enumerate(equips, 1)]
                    api.say("◆ 神速　请选择弃置一张装备牌: " + "　".join(parts) + " (回序号), 0=取消")
                    return True
                elif phase == 3:
                    me["shensu_used_3"] = True
                    st["flipped_you"] = True
                    api.say("◆ 神速　你跳过弃牌阶段，翻面，视为使用【杀】")
                    virtual = {"n": "杀", "s": "", "r": "", "i": -1}
                    api.game._resolve_sha(virtual)
                    if not st.get("pending") and not st["over"]:
                        api.game._end_phase("you")
                    else:
                        st["_shensu_after"] = "discard"
                    return True
            return True

        elif t == "shensu_pick":
            if text in ("0", "过", "取消"):
                api.say("◆ 神速　取消")
                st["pending"] = None
                return True
            idx = int(text) if text.isdigit() else 0
            equips = [c for c in me["hand"] if c["n"] in WEAPONS or c["n"] in ARMORS or c["n"] in ("-1马", "+1马")]
            if idx < 1 or idx > len(equips):
                api.say("◆ 提示　序号不对")
                return True

            eq = equips[idx - 1]
            me["hand"] = [x for x in me["hand"] if x["i"] != eq["i"]]
            st["discard"].append(eq)
            st["pending"] = None
            me["shensu_used_2"] = True
            st["jp"]["skip_play"] = True
            api.say(f"◆ 神速　你弃置 {eq['s']}{eq['r']}{eq['n']}，视为使用【杀】")
            virtual = {"n": "杀", "s": "", "r": "", "i": -1}
            api.game._resolve_sha(virtual)
            if not st.get("pending") and not st["over"]:
                api.game._end("you")
            else:
                st["_shensu_after"] = "play"
            return True
        return None


@skill("整辎")
class Zhengzi:
    """整辎：当你本回合造成了X点伤害后，你回复1点体力值(X为你当前的体力值)。"""
    def on_turn_start(self, api):
        api.me["_zhengyi_dmg"] = 0
        api.me["_zhengyi_healed"] = False

    def on_damage_dealt(self, api, target_who, dmg, card, element):
        me = api.me
        me["_zhengyi_dmg"] = me.get("_zhengyi_dmg", 0) + dmg
        if me["_zhengyi_dmg"] >= me["hp"] and not me.get("_zhengyi_healed"):
            if me["hp"] < me["maxhp"]:
                me["_zhengyi_healed"] = True
                api.game.heal(1)
                api.say(f"◆ 整辎　本回合造成伤害达到{me['hp']}点,回复1点体力")


@skill("诈死")
class Zhasi:
    """诈死：出牌阶段限一次，你可以弃置一张牌并失去1点体力，然后摸三张牌，本回合杀使用次数+1。"""
    def on_turn_start(self, api):
        api.me["zhasi_used"] = False

    def on_skill(self, api, key):
        if key != "zhasi":
            return None
        st = api.state
        me = api.me
        if me.get("zhasi_used"):
            api.say("◆ 提示　诈死本回合已用过")
            return True
        if not api.hand:
            api.say("◆ 提示　没手牌,不能发动诈死")
            return True

        me["zhasi_used"] = True
        st["pending"] = {"t": "zhasi_pick", "who": "you"}
        api.say("◆ 诈死　请弃置一张牌发动(回序号),0=取消")
        return True

    def on_ai_action(self, api):
        me = api.me
        if me.get("zhasi_used"):
            return None
        if not api.hand:
            return None
        if me["hp"] <= 1:
            return None

        me["zhasi_used"] = True
        worst = sorted(api.hand, key=lambda x: 0 if x["n"] not in ("桃", "无懈可击", "杀", "闪") else 1)[0]
        api.game._discard(api.who, worst)
        api.say(f"◆ 诈死　我弃置 {worst['s']}{worst['r']}{worst['n']}")

        me["hp"] -= 1
        api.say(f"◆ 诈死　我失去1点体力,回到 {me['hp']}")
        api.draw(3)
        api.state["sha_limit_bonus"] += 1
        api.say("◆ 诈死　摸3张牌,本回合杀次数+1")

        if me["hp"] <= 0:
            api.game.dying(api.who)
            return True
        return None

    def on_pending(self, api, pending, text):
        if pending.get("t") != "zhasi_pick":
            return None
        st = api.state
        you = st["you"]
        if text in ("0", "过", "取消"):
            api.say("◆ 诈死　取消")
            you["zhasi_used"] = False
            st["pending"] = None
            return True
        c = api.game._hand(int(text)) if text.isdigit() else None
        if not c:
            api.say("◆ 提示　回手牌序号或0")
            return True

        st["pending"] = None
        api.game._discard("you", c)
        api.say(f"◆ 诈死　你弃置 {c['s']}{c['r']}{c['n']}")

        you["hp"] -= 1
        api.say(f"◆ 诈死　你失去1点体力,回到 {you['hp']}")
        api.draw(3)
        st["sha_limit_bonus"] += 1
        api.say("◆ 诈死　摸3张牌,本回合杀次数+1")

        if you["hp"] <= 0:
            api.game.dying("you")
        return True


@skill("水淹七军")
class Shuiyan:
    """水淹七军：出牌阶段限一次，你可以弃置一张锦囊牌，令一名角色选择弃置其区域内所有装备牌或受到1点伤害。"""
    def on_turn_start(self, api):
        api.me["shuiyan_used"] = False

    def on_skill(self, api, key):
        if key != "shuiyan":
            return None
        st = api.state
        me = api.me
        if me.get("shuiyan_used"):
            api.say("◆ 提示　水淹七军本回合已用过")
            return True

        tricks = [c for c in api.hand if c["n"] in api.game.TRICKS_ACTIVE or c["n"] == "铁索连环"]
        if not tricks:
            api.say("◆ 提示　没有锦囊牌,不能发动水淹七军")
            return True

        me["shuiyan_used"] = True
        st["pending"] = {"t": "shuiyan_pick", "who": "you"}
        api.say("◆ 水淹七军　回一张锦囊牌序号弃置,0=取消")
        return True

    def on_ai_action(self, api):
        st = api.state
        me = api.me
        you = st["you"]

        if me.get("shuiyan_used"):
            return None

        tricks = [c for c in api.hand if c["n"] in api.game.TRICKS_ACTIVE or c["n"] == "铁索连环"]
        if not tricks:
            return None

        if not you["equip"] and you["hp"] > 1:
            return None

        me["shuiyan_used"] = True
        c = tricks[0]
        api.game._hand_out(api.who, c)
        st["discard"].append(c)
        api.say(f"◆ 水淹七军　我弃置锦囊 {c['s']}{c['r']}{c['n']} 发动水淹七军")

        if you["equip"]:
            st["pending"] = {"t": "shuiyan_opt", "who": "you"}
            api.say("◆ 水淹七军　请选择: 1=受到1点伤害; 2=弃置区域内所有装备牌")
            return True
        else:
            api.say("◆ 水淹七军　你无装备可弃,受到1点伤害")
            api.game.hurt("you", 1, "me")
            return True

    def on_pending(self, api, pending, text):
        t = pending.get("t")
        if t not in ("shuiyan_pick", "shuiyan_opt"):
            return None

        st = api.state
        you = st["you"]
        me = st["me"]

        if t == "shuiyan_pick":
            if text in ("0", "过", "取消"):
                st["pending"] = None
                you["shuiyan_used"] = False
                api.say("◆ 水淹七军　取消")
                return True
            c = api.game._hand(int(text)) if text.isdigit() else None
            if not c or (c["n"] not in api.game.TRICKS_ACTIVE and c["n"] != "铁索连环"):
                api.say("◆ 提示　回锦囊牌序号或0")
                return True

            st["pending"] = None
            api.game._discard("you", c)
            api.say(f"◆ 水淹七军　你弃置锦囊 {c['s']}{c['r']}{c['n']}")

            if me["equip"]:
                if me["hp"] <= 2 or len(me["equip"]) > 1:
                    eq_list = list(me["equip"].values())
                    for eq in eq_list:
                        api.game._discard("me", eq)
                    api.say("◆ 水淹七军　我选择弃置所有装备牌")
                else:
                    api.say("◆ 水淹七军　我选择受到1点伤害")
                    api.game.hurt("me", 1, "you")
            else:
                api.say("◆ 水淹七军　我无装备可弃,受到1点伤害")
                api.game.hurt("me", 1, "you")
            return True

        elif t == "shuiyan_opt":
            if text in ("1", "0", "过", "受伤", ""):
                st["pending"] = None
                api.say("◆ 水淹七军　你选择受到1点伤害")
                api.game.hurt("you", 1, "me")
                if not st["over"] and st["turn"] == "me":
                    api.game._ai_play()
                return True

            if text == "2":
                if not you["equip"]:
                    st["pending"] = None
                    api.say("◆ 提示　你无装备可弃,受到1点伤害")
                    api.game.hurt("you", 1, "me")
                else:
                    st["pending"] = None
                    eq_list = list(you["equip"].values())
                    for eq in eq_list:
                        api.game._discard("you", eq)
                    api.say("◆ 水淹七军　你弃置了所有装备牌")

                if not st["over"] and st["turn"] == "me":
                    api.game._ai_play()
                return True

            api.say("◆ 提示　请输入 1=受到1点伤害, 2=弃置所有装备牌")
            return True

        return None