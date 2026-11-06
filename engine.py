# -*- coding: utf-8 -*-
import random
import re

from .heroes import HEROES, SKILL_DESC, D

from .skill2 import (
    dispatch as s2_dispatch,
    dispatch_first as s2_dispatch_first,
    import_all_skills as s2_import_all,
)
from .skill_api import SkillAPI

s2_import_all()

SUITS = ["♠", "♥", "♣", "♦"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
WEAPONS = ["诸葛连弩", "青釭剑", "雌雄双股剑", "寒冰剑", "古锭刀", "青龙偃月刀", "贯石斧", "方天画戟", "麒麟弓", "丈八蛇矛"]
ARMORS = ["八卦阵", "仁王盾", "藤甲", "白银狮子"]
WEAPON_RANGE = {"诸葛连弩": 1, "青釭剑": 2, "雌雄双股剑": 2, "寒冰剑": 2, "古锭刀": 2, "青龙偃月刀": 3, "贯石斧": 3, "丈八蛇矛": 3, "方天画戟": 4, "麒麟弓": 5}
ARMOR_RANK = {"八卦阵": 4, "仁王盾": 3, "藤甲": 2, "白银狮子": 1}
NAMES = (["杀"] * 30 + ["火杀"] * 5 + ["雷杀"] * 9 + ["闪"] * 15 + ["桃"] * 8 + ["酒"] * 5
    + ["过河拆桥"] * 6 + ["顺手牵羊"] * 5 + ["无中生有"] * 4 + ["南蛮入侵"] * 3 + ["决斗"] * 3 + ["乐不思蜀"] * 3
    + ["无懈可击"] * 3 + ["闪电"] * 2 + ["五谷丰登"] * 2 + ["借刀杀人"] * 2 + ["万箭齐发"] * 1 + ["桃园结义"] * 1
    + ["火攻"] * 3 + ["铁索连环"] * 6 + ["兵粮寸断"] * 2
    + ["八卦阵"] * 2 + ["仁王盾"] * 1 + ["藤甲"] * 2 + ["白银狮子"] * 1 + ["-1马"] * 3 + ["+1马"] * 3
    + ["诸葛连弩"] * 2 + ["青釭剑"] * 1 + ["雌雄双股剑"] * 1 + ["寒冰剑"] * 1 + ["古锭刀"] * 1 + ["贯石斧"] * 1
    + ["青龙偃月刀"] * 1 + ["丈八蛇矛"] * 1 + ["方天画戟"] * 1 + ["麒麟弓"] * 1)
PROMPT = {
    "discard": "弃牌阶段:回要弃的序号(空格分开)",
    "shan": "需要出闪:回序号,0=不出",
    "sha": "需要出杀:回序号,0=不出",
    "duel": "决斗:回杀的序号,0=认输",
    "jiedao": "借刀:回杀的序号作为响应,0=不出杀交出武器",
    "dying": "濒死:回桃/酒的序号,0=放弃",
    "wugu": "五谷:回1或2取牌",
    "qingnang": "青囊:回要弃的手牌序号",
    "guose": "国色:回一张方块手牌序号",
    "qixi": "奇袭:回一张黑色手牌序号",
    "wusheng": "武圣:回一张红色手牌序号当杀使用,0=取消",
    "zhiheng": "制衡:回要弃的序号(空格分开)",
    "fanjian": "反间:回一张要扣至手中的手牌序号",
    "fanjian_guess": "反间:回1=♠ 2=♥ 3=♣ 4=♦ 猜花色",
    "yijue_show": "义绝:请展示一张手牌,回序号",
    "guanxing": "观星:顶1 2 3=全放顶;顶1 底2 3=1顶2和3底;底1 2 3=全放底",
    "guanshi": "贯石斧:回两张手牌序号强命中,0=算了",
    "yinghun": "英魂:A=令对手摸1弃X,0=不发动",
    "yinghun_pick": "英魂:回要弃的序号(空格分开),装备用A/B/C/D,如1 4 A;0=放弃",
    "huogong": "火攻:回同花色手牌序号弃置,0=算了",
    "huogong_show": "火攻:回要展示的手牌序号",
    "hanbing": "寒冰剑:1=防止伤害改弃对方2张,0=正常伤害",
    "tiesuo": "铁索连环:1=横置对手 2=重铸摸牌 0=取消",
    "zhangba": "丈八蛇矛:回两张手牌序号(空格分开)当杀,0=取消",
    "qimou": "奇谋:回要失去的体力数,0=取消",
    "kuanggu": "狂骨:1=回复1点体力 2=摸一张牌",
    "yijue": "义绝:回要弃置的手牌序号,0=取消",
    "luoyi_opt": "裸衣:1=发动 0=放弃",
    "luoyi_pick": "裸衣:回要弃的手牌序号,0=放弃",
    "qingjian_opt": "清俭:1=获得这张牌 0=放弃(放弃不消耗本轮次数)",
    "guicai_opt": "鬼才:回手牌序号替换判定,0=不改",
    "cixiong": "雌雄双股剑:回手牌序号=弃牌,0=让使用者摸一张",
    "wuxie_wugu": "无懈五谷:回无懈可击序号阻止对手取牌,0=放行",
    "wuxie_wugu_ai": "无懈五谷:回无懈可击序号阻止我取牌,0=放行",
    "drawopt": "摸牌阶段:字母发动技能,0=正常摸2张",
    "pick": "选将:1/2/3选自己；A=指定自己 B=指定敌人 0=用已指定开始",
    "pick_self_name": "回要指定给自己使用的武将名(0=取消)",
    "pick_opp_name": "回要让敌人使用的武将名(0=取消)",
    "target": "选牌:回数字,手牌项随机抽取",
    "wuxie": "无懈窗口:回无懈可击的序号抵消/0放行",
    "restart": "回确认放弃当前战局",
    "jushou_opt": "据守:1=发动(翻面摸4弃1,弃装备则穿戴) 0=放弃",
    "jushou_discard": "据守:回要弃的手牌序号(装备牌会改为穿戴)",
    "tieqi_discard": "铁骑:回同花色手牌序号弃掉换出闪,0=不弃直接受伤",
}

def _names(hero):
    return [s[0] for s in hero["s"]]

def has(ch, skill):
    return ch["hero"] and skill in _names(ch["hero"])

def armor(ch):
    a = ch["equip"].get("armor")
    return a["n"] if a else None

def wep(ch):
    w = ch["equip"].get("weapon")
    return w["n"] if w else None

def other(w):
    return "me" if w == "you" else "you"

def attack_range(ch):
    w = ch["equip"].get("weapon")
    return WEAPON_RANGE.get(w["n"], 1) if w else 1

def distance(src, dst):
    d = 1
    if src["equip"].get("minus"):
        d -= 1
    if has(src, "马术"):
        d -= 1
    if dst["equip"].get("plus"):
        d += 1
    return max(d, 1)

def in_attack_range(src, dst):
    return distance(src, dst) <= attack_range(src)

def elem_of(card):
    n = card.get("n")
    if n == "火杀":
        return "fire"
    if n == "雷杀":
        return "thunder"
    return None

def has_judge(who, name):
    return any(c["n"] == name for c in who["judge"])

class Game:
    @staticmethod
    def _opp(who):
        return "me" if who == "you" else "you"

    def __init__(self):
        self.reset()

    def reset(self):
        self.deck = self._build()
        pool = HEROES[:]
        random.shuffle(pool)
        self.st = {
            "you": {"hero": None, "hp": 0, "maxhp": 0, "hand": [], "equip": {}, "judge": [], "chained": False},
            "me": {"hero": None, "hp": 0, "maxhp": 0, "hand": [], "equip": {}, "judge": [], "chained": False},
            "turn": "you", "pending": None, "over": None,
            "sha_used": 0, "me_sha_used": 0, "luoyi": False, "reveal": None,
            "zhiheng_used": False, "fanjian_used": False, "qixi_used": False,
            "qingjian_used_you": False, "qingjian_used_me": False,
            "jieyin_used_you": False, "jieyin_used_me": False,
            "yijue_used": False, "yajiao_used": False, "qimou_used": False,
            "sha_limit_bonus": 0, "distance_bonus": 0, "yijue_buff": False,
            "liyong_you": False, "liyong_me": False,
            "jiu": False, "jiu_used": False,
            "discard": [], "wx": None, "jp": None,
            "first_player": None, "turn_count": 0,
            "_in_ai_play": False, "_ai_need_rerun": False, "pending_after": [],
            "_flavor_dying_you": False, "_flavor_dying_me": False,
            "flipped_you": False, "flipped_me": False,
            "pick": {"you": pool[:3], "me": pool[3:6]},
            "pick_custom": {"you": None, "me": None},
        }
        self.msg = []
        self.history = []
        self.first_view = True
        self.llm_events = []

    @staticmethod
    def _build():
        combos = [(s, r) for s in SUITS for r in RANKS] * 2
        allc = [(s, r) for s in SUITS for r in RANKS]
        while len(combos) < len(NAMES):
            combos.append(random.choice(allc))
        combos = combos[:len(NAMES)]
        random.shuffle(combos)
        names = NAMES[:]
        random.shuffle(names)
        return [{"i": i, "s": c[0], "r": c[1], "n": n} for i, (c, n) in enumerate(zip(combos, names))]

    def _gender(self, ch):
        if not ch["hero"]:
            return "M"
        return ch["hero"].get("g", "M")

    def say(self, t):
        t = t.replace("。", ",")
        you_h = self.st["you"]["hero"]
        me_h = self.st["me"]["hero"]
        if you_h and me_h:
            t = t.replace("你", you_h["n"]).replace("我", me_h["n"])
        self.msg.append(t)
        if not t.startswith("◆ 提示"):
            self.history.append(t)
            if len(self.history) > 24:
                self.history = self.history[-24:]

    def _snapshot(self, kind, extra=""):
        st = self.st
        you, me = st["you"], st["me"]
        def _ch(ch):
            return {
                "hero": ch["hero"]["n"] if ch["hero"] else "?",
                "hp": max(ch["hp"], 0),
                "maxhp": ch["maxhp"],
                "hand": len(ch["hand"]),
                "equip": [v["n"] for v in ch["equip"].values()],
                "judge": [c["n"] for c in ch["judge"]],
            }
        desc_map = {
            "start_me_first": "游戏开局，你(AI)先手",
            "start_you_first": "游戏开局，对手先手",
            "me_hit": f"你对对手造成了{extra}伤害",
            "you_hit": f"对手对你造成了{extra}伤害",
            "me_big_hit": f"你对对手造成了{extra}大伤害",
            "you_big_hit": f"对手对你造成了{extra}大伤害",
            "me_dying": "你(AI)濒死",
            "you_dying": "对手濒死",
            "me_win": "你(AI)获胜，对手阵亡",
            "you_win": "对手获胜，你(AI)阵亡",
            "you_sha": f"对手对你使用杀{extra}",
            "me_sha": f"你对对手使用杀{extra}",
            "you_trick": f"对手使用锦囊{extra}",
            "me_trick": f"你使用锦囊{extra}",
            "you_end_turn": "对手结束出牌回合",
            "me_end_turn": "你结束出牌回合",
            "you_turn_start": "轮到对手出牌",
            "me_turn_start": "轮到你出牌",
            "you_heal": "对手回复体力",
            "me_heal": "你回复体力",
        }
        has_h = bool(you["hero"] and me["hero"])
        return {
            "kind": kind,
            "desc": desc_map.get(kind, kind + extra),
            "you": _ch(you),
            "me": _ch(me),
            "turn": st["turn"],
            "turn_count": st.get("turn_count", 0),
            "first_player": st.get("first_player"),
            "pending": (st["pending"] or {}).get("t"),
            "distance_you_to_me": distance(you, me) if has_h else None,
            "distance_me_to_you": distance(me, you) if has_h else None,
            "attack_range_you": attack_range(you) if has_h else None,
            "attack_range_me": attack_range(me) if has_h else None,
        }

    def _flavor(self, key, extra=""):
        you, me = self.st["you"], self.st["me"]
        if not (you["hero"] and me["hero"]):
            return
        self.llm_events.append(self._snapshot(key, extra))

    def take_llm_events(self):
        ev = self.llm_events[:]
        self.llm_events.clear()
        return ev

    def build_llm_prompt(self, event) -> str:
        m = event["me"]
        y = event["you"]
        me_equip = "、".join(m["equip"]) or "无"
        you_equip = "、".join(y["equip"]) or "无"
        me_judge = "、".join(m["judge"]) or "无"
        you_judge = "、".join(y["judge"]) or "无"

        hp_diff = m["hp"] - y["hp"]
        if hp_diff >= 2:
            hp_state = f"你领先 {hp_diff} 点血，占优"
        elif hp_diff <= -2:
            hp_state = f"你落后 {-hp_diff} 点血，危急"
        else:
            hp_state = "双方血量接近，胶着"

        card_diff = m["hand"] - y["hand"]
        if card_diff >= 3:
            card_state = f"你手牌多 {card_diff} 张，资源充足"
        elif card_diff <= -3:
            card_state = f"你手牌少 {-card_diff} 张，资源紧张"
        else:
            card_state = "手牌数接近"

        dist = event.get("distance_me_to_you")
        rng = event.get("attack_range_me")
        range_state = ""
        if dist is not None and rng is not None:
            if dist > rng:
                range_state = f"你的攻击范围 {rng} 够不到对手（距离 {dist}）"
            else:
                range_state = f"你的攻击范围 {rng} 能打到对手（距离 {dist}）"

        recent = ""
        if self.history:
            recent = "\n最近几手：\n" + "\n".join(
                "- " + h.lstrip("◆ ").strip() for h in self.history[-5:]
            ) + "\n"

        return (
            f"你正在和玩家玩三国杀 1v1 单挑，你操控【{m['hero']}】，对手【{y['hero']}】。\n\n"
            f"当前局势：\n"
            f"- 你：{m['hp']}/{m['maxhp']} 血 · {m['hand']} 张牌 · 装备 {me_equip} · 判定 {me_judge}\n"
            f"- 对手：{y['hp']}/{y['maxhp']} 血 · {y['hand']} 张牌 · 装备 {you_equip} · 判定 {you_judge}\n"
            f"- 第 {event['turn_count']} 回合 · 现在轮到 {event.get('turn', '?')} 出牌\n"
            f"- 局势判断：{hp_state}；{card_state}" + (f"；{range_state}" if range_state else "") + "\n"
            f"{recent}\n"
            f"刚刚发生：{event['desc']}\n\n"
            f"请用你自己的人格、你自己的口吻，说一句此刻的反应（不超过 40 字）。\n"
            f"要求：\n"
            f"1. 必须结合具体局势（血差/牌差/距离/装备/判定/刚发生的事，至少提一个具体数字或事实），不要泛泛而谈\n"
            f"2. 语气随局势变化：领先可得意、落后可嘴硬或示弱、濒死可悲壮、被阴可吐槽、优势被翻可不服\n"
            f"3. 不要刻意模仿三国武将，你操控的是这个武将，但说话的是你自己\n"
            f"4. 不要叙述动作，不要复述事件本身（禁止写「我受到伤害」「我赢了」这类）\n"
            f"5. 不加引号、括号、前缀「◆」，不解释，只输出一句话\n"
        )

    def draw(self, who, n=1):
        out = []
        for _ in range(n):
            if not self.deck:
                self.deck = self.st.get("discard", [])
                self.st["discard"] = []
                random.shuffle(self.deck)
            if not self.deck:
                break
            c = self.deck.pop()
            self.st[who]["hand"].append(c)
            out.append(c)
        return out

    @staticmethod
    def blood(ch):
        return "".join("●" if i < max(ch["hp"], 0) else "○" for i in range(ch["maxhp"]))

    def _name(self, who):
        ch = self.st[who]
        if ch["hero"]:
            return ch["hero"]["n"]
        return "你" if who == "you" else "我"

    def view(self):
        st = self.st
        you, me = st["you"], st["me"]
        p = st["pending"]
        BAR = "──────────────"
        you_name = self._name("you")
        me_name = self._name("me")
        L = []
        if p and p["t"] == "pick":
            L.append("◆ 选将")
            for i, h in enumerate(st["pick"]["you"], 1):
                L.append(f"　{i}　{h['n']}　{h['hp']}血")
                for name, timing, key in h["s"]:
                    L.append(f"　　　{name}({timing}):{SKILL_DESC.get(key, '')}")
            custom = st.get("pick_custom") or {}
            you_c = custom.get("you")
            me_c = custom.get("me")
            L.append("◆ 已指定")
            L.append(f"　你的武将: {you_c['n'] if you_c else '未指定'}")
            L.append(f"　敌人武将: {me_c['n'] if me_c else '未指定'}")
            L.append("◆ 选项　1/2/3=从候选选自己(敌人随机)；A=指定自己 B=指定敌人；0=用已指定开始")
            return "\n".join(L)
        if p and p["t"] == "pick_self_name":
            L.append("◆ 选将　指定自己的武将")
            L.append("◆ 提示　回要给自己使用的武将名(0=取消)")
            return "\n".join(L)
        if p and p["t"] == "pick_opp_name":
            L.append("◆ 选将　指定敌人使用的武将")
            L.append("◆ 提示　回要让敌人使用的武将名(0=取消)")
            return "\n".join(L)
        eq = lambda ch: "　".join(ch["equip"][k]["n"] for k in ("weapon", "armor", "minus", "plus") if k in ch["equip"]) or "—"
        jd = []
        for w in ("you", "me"):
            wname = you_name if w == "you" else me_name
            for c in st[w]["judge"]:
                jd.append(f"{wname}:{c['n']}")
        chain = []
        if you.get("chained"):
            chain.append(you_name)
        if me.get("chained"):
            chain.append(me_name)
        L.append(BAR)
        L.append("◆ 局势")
        you_flip = "  [翻面]" if st.get("flipped_you") else ""
        me_flip = "  [翻面]" if st.get("flipped_me") else ""
        L.append(f"　{you_name}　{self.blood(you)}　{len(you['hand'])}牌{you_flip}")
        L.append(f"　{me_name}　{self.blood(me)}　{len(me['hand'])}牌{me_flip}")
        L.append(f"◆ 距离　{you_name}到{me_name} {distance(you, me)}　{me_name}到{you_name} {distance(me, you)}")
        L.append(f"◆ 攻击范围　{you_name} {attack_range(you)}　{me_name} {attack_range(me)}")
        L.append("◆ 判定　" + ("　".join(jd) if jd else "无"))
        L.append(f"◆ 装备　{you_name}:{eq(you)}　{me_name}:{eq(me)}")
        if chain:
            L.append("◆ 铁索　横置:" + "、".join(chain))
        if st["over"]:
            if st["over"] == "you":
                phase = f"{you_name}赢了,{me_name}躺了"
            else:
                phase = f"{me_name}赢了,{you_name}认命吧"
        elif p:
            phase = PROMPT.get(p["t"], "等你回数字")
        elif st["turn"] == "you":
            phase = f"{you_name}出牌"
        else:
            phase = f"{me_name}行动"
        L.append(f"◆ 阶段　{phase}")
        L.append(BAR)
        L.append("◆ 武将")
        L.append(f"　{you_name}　{max(you['hp'], 0)}/{you['maxhp']}")
        L.append(f"　{me_name}　{max(me['hp'], 0)}/{me['maxhp']}")
        L.append(BAR)
        L.append(f"◆ 手牌({you_name})")
        if you["hand"]:
            for i, c in enumerate(you["hand"], 1):
                L.append(f"　{i}　{c['s']}{c['r']}　{c['n']}")
        else:
            L.append("　无")
        if p and p.get("opts_line"):
            L.append("◆ 选择　" + p["opts_line"])
        if st["reveal"]:
            L.append("◆ 五谷　" + "　".join(f"{i}={c['s']}{c['r']}{c['n']}" for i, c in enumerate(st["reveal"], 1)))
        has_skill = (you["hero"] and you["hero"]["s"]) or wep(you) == "丈八蛇矛"
        if has_skill:
            L.append(BAR)
            L.append("◆ 技能")
            if you["hero"] and you["hero"]["s"]:
                for i, (n, t, key) in enumerate(you["hero"]["s"]):
                    L.append(f"　{'ABCDE'[i]}　{n}　{t}")
                    desc = SKILL_DESC.get(key, "")
                    if desc:
                        L.append(f"　　　{desc}")
            if wep(you) == "丈八蛇矛":
                L.append("　&　丈八蛇矛　出牌阶段")
                L.append(f"　　　{SKILL_DESC.get('zhangba_skill', '')}")
        if st["over"]:
            L.append(BAR)
            L.append(f"◆ {me_name}的手牌(游戏已结束)")
            if me["hand"]:
                for i, c in enumerate(me["hand"], 1):
                    L.append(f"　{i}　{c['s']}{c['r']}　{c['n']}")
            else:
                L.append("　无")
            L.append("◆ 输入任意内容立即开始新一局")
        L.append(BAR)
        if p:
            if p["t"] == "shan" and p.get("no_shan"):
                prompt = f"{p.get('reason', '厉勇')}:目标不可响应,直接掉血"
            elif p["t"] == "shan" and p.get("qb"):
                prompt = "需要出闪:回序号;#或八卦=八卦阵判定;0=不出"
            else:
                prompt = PROMPT.get(p["t"], "回数字")
            L.append("◆ 选项　" + prompt + "　?=说明")
        elif st["turn"] == "you" and not st["over"]:
            hint = "数字=出牌　字母=用技能"
            if wep(you) == "丈八蛇矛":
                hint += "　&=丈八蛇矛"
            hint += "　0=结束出牌　?=说明"
            L.append("◆ 选项　" + hint)
        else:
            L.append(f"◆ 选项　等{me_name}行动")
        return "\n".join(L)

    def skills_line(self):
        ch = self.st["you"]
        if not ch["hero"]:
            return ""
        parts = []
        for i, (n, t, key) in enumerate(ch["hero"]["s"]):
            parts.append(f"{'ABCDE'[i]} {n}·{t}:{SKILL_DESC.get(key, '')}")
        if wep(ch) == "丈八蛇矛":
            parts.append(f"& 丈八蛇矛·出牌阶段:{SKILL_DESC.get('zhangba_skill', '')}")
        return "◆ 技能\n" + "\n".join(parts)

    def out(self, extra=None):
        body = []
        if self.msg:
            body.extend(self.msg)
            self.msg.clear()
        if extra:
            body.append(extra)
        only_hints = bool(body) and all(m.startswith("◆ 提示") for m in body)
        if only_hints and not extra:
            self.first_view = False
            return "\n".join(x for x in body if x)
        body.append(self.view())
        self.first_view = False
        return "\n".join(x for x in body if x)

    def _resume_ai_if_needed(self):
        st = self.st
        if not st["over"] and st["turn"] == "me" and not st["pending"]:
            self._ai_play()

    def _pop_pending_after(self):
        st = self.st
        st["pending"] = None
        q = st.get("pending_after", [])
        while q:
            nxt = q.pop(0)
            t = nxt.get("t")
            if t == "ganglie_pick":
                src = nxt["dmg_src"]
                if not st[src]["hand"]:
                    continue
                if len(st[src]["hand"]) < 2:
                    self.say("◆ 刚烈　来源手牌不足,受1点")
                    self.hurt(src, 1)
                    if st.get("pending") or st["over"]:
                        return True
                    continue
                st["pending"] = nxt
                self.say("◆ 刚烈　你要弃2张手牌(回2个序号),或回0改为受1点伤害")
                return True
            if t == "kuanggu":
                st["pending"] = nxt
                self.say("◆ 狂骨　1=回复1点体力 2=摸一张牌")
                return True
            if t == "fankui":
                st["pending"] = nxt
                self.say("◆ 反馈　回显示的编号")
                return True
            if t == "luoyi_opt":
                st["pending"] = nxt
                self.say("◆ 裸衣　1=发动 0=放弃")
                return True
        return False

    def start(self):
        self.say("◆ 开局　各发 3 张武将牌,回 1/2/3 选；A=指定自己 B=指定敌人 0=用已指定开始")
        self.st["pending"] = {"t": "pick"}
        self.st["pick_custom"] = {"you": None, "me": None}
        return self.out()

    def pick(self, idx):
        st = self.st
        custom = st.get("pick_custom") or {}
        h = custom.get("you") or st["pick"]["you"][idx]
        mh = custom.get("me") or random.choice(st["pick"]["me"])
        return self._do_pick(h, mh)

    def _do_pick(self, h, mh):
        st = self.st
        for side, hero in (("you", h), ("me", mh)):
            ch = st[side]
            ch["hero"] = {"n": hero["n"], "hp": hero["hp"], "s": hero["s"], "g": hero.get("g", "M")}
            ch["hp"] = ch["maxhp"] = hero["hp"]
        st["pending"] = None
        first = random.choice(["you", "me"])
        st["first_player"] = first
        second = "me" if first == "you" else "you"
        self.draw(first, 4)
        self.draw(second, 5)
        st["discard"] = []
        first_name = f"{h['n']}先手" if first == "you" else f"{mh['n']}先手"
        self.say(f"◆ 选将　{first_name}(先手4张,后手5张)")
        if first == "me":
            self._flavor("start_me_first")
        else:
            self._flavor("start_you_first")
        self._turn(first)
        return self.out()

    def _pick_start_custom(self):
        st = self.st
        custom = st.get("pick_custom") or {}
        h = custom.get("you")
        mh = custom.get("me")
        if not h and not mh:
            return "◆ 提示　未指定任何武将，请按 1/2/3 选择或 A/B 指定"
        if not h:
            h = random.choice(st["pick"]["you"])
        if not mh:
            mh = random.choice(st["pick"]["me"])
        return self._do_pick(h, mh)

    @staticmethod
    def _valuable_card(card):
        return card["n"] in ("杀", "闪", "桃", "酒", "火杀", "雷杀") or card["n"] in WEAPONS or card["n"] in ARMORS or card["n"] in ("无懈可击", "无中生有")

    def _to_discard(self, card, allow_pending=True, is_play=False, is_judge=False):
        if self.st.get("over"):
            self.st["discard"].append(card)
            return
        if not is_play:
            for side in ("you", "me"):
                for r in s2_dispatch(self, side, "on_card_to_discard", SkillAPI(self, side), card, is_play, is_judge):
                    if r:
                        return
        you = self.st["you"]
        me = self.st["me"]
        if is_judge or is_play:
            self.st["discard"].append(card)
            return
        if allow_pending and you["hero"] and has(you, "清俭") and not self.st.get("qingjian_used_you"):
            pending = self.st.get("pending")
            if pending and pending.get("t") == "qingjian_opt":
                pending.setdefault("queue", []).append(card)
            else:
                self.st["pending"] = {"t": "qingjian_opt", "card": card, "queue": []}
            self.say(f"◆ 清俭　你可以获得 {card['s']}{card['r']}{card['n']},1=获得 0=放弃(放弃不消耗本轮次数)")
            return
        if me["hero"] and has(me, "清俭") and not self.st.get("qingjian_used_me"):
            if self._valuable_card(card):
                me["hand"].append(card)
                self.st["qingjian_used_me"] = True
                self.say(f"◆ 清俭　我获得 {card['s']}{card['r']}{card['n']}")
                return
        self.st["discard"].append(card)

    def judge(self, who, why):
        if not self.deck:
            self.deck = self.st.get("discard", [])
            self.st["discard"] = []
            random.shuffle(self.deck)
        if not self.deck:
            return {"i": -1, "s": "♠", "r": "A", "n": "无"}
        c = self.deck.pop()
        self.say(f"◆ 判定　{'你' if who == 'you' else '我'} {c['s']}{c['r']}({why})")
        ch = self.st[who]
        _api_s2 = SkillAPI(self, who)
        _repl = s2_dispatch_first(self, who, "on_judge_replace", _api_s2, c, why, default=None)
        if _repl is not None:
            self._to_discard(c, allow_pending=False, is_judge=True)
            c = _repl
            self.say(f"◆ 判定替换　{c['s']}{c['r']}{c['n']}")
        s2_dispatch(self, who, "on_judge_after", _api_s2, c, why)
        if has(ch, "天妒"):
            ch["hand"].append(c)
            self.say(f"◆ 天妒　{'你' if who == 'you' else '我'}获得判定牌 {c['s']}{c['r']}{c['n']}")
            return c
        self._to_discard(c, allow_pending=False, is_judge=True)
        return c

    def luoshen(self, who):
        ch = self.st[who]
        got = 0
        for _ in range(10):
            j = self.judge(who, "洛神")
            if j["i"] == -1:
                break
            if j["s"] in ("♠", "♣"):
                if not any(x["i"] == j["i"] for x in ch["hand"]):
                    self.st["discard"] = [x for x in self.st["discard"] if x["i"] != j["i"]]
                    ch["hand"].append(j)
                got += 1
                self.say("◆ 洛神　黑色,入手中,继续")
            else:
                self.say("◆ 洛神　判红,停止")
                break
        if got:
            self.say(f"◆ 洛神　共得 {got} 张")

    def _build_pick_opts(self, src):
        sc = self.st[src]
        opts = []
        if sc["hand"]:
            opts.append((0, "hand", None, "随机手牌"))
        slot_list = [("weapon", 1, "武器"), ("armor", 2, "防具"), ("minus", 3, "-1马"), ("plus", 4, "+1马")]
        for k, num, name in slot_list:
            v = sc["equip"].get(k)
            if v:
                opts.append((num, "equip", k, f"{v['s']}{v['r']}{v['n']}({name})"))
        return opts

    def _ai_cixiong_choice(self, target, atk):
        th = self.st[target]
        atk_name = "你" if atk == "you" else "我"
        tgt_name = "你" if target == "you" else "我"
        if len(th["hand"]) >= 2:
            worst = sorted(th["hand"], key=lambda x: 0 if x["n"] not in ("桃", "无懈可击", "杀", "闪") else 1)[0]
            self._hand_out(target, worst)
            self.st["discard"].append(worst)
            self.say(f"◆ 雌雄双股剑　{tgt_name}弃 {worst['s']}{worst['r']}{worst['n']}")
        else:
            self.draw(atk, 1)
            self.say(f"◆ 雌雄双股剑　{tgt_name}让{atk_name}摸一张")

    def _check_jieyin(self):
        st = self.st
        for side in ("you", "me"):
            ch = st[side]
            if ch["hero"] and has(ch, "结姻") and not st.get(f"jieyin_used_{side}"):
                st[f"jieyin_used_{side}"] = True
                self.draw(side, 1)
                self.say(f"◆ 结姻　有角色回复体力,{'你' if side == 'you' else '我'}摸1张")

    def _hand_out(self, who, card):
        ch = self.st[who]
        before = len(ch["hand"])
        ch["hand"] = [c for c in ch["hand"] if c["i"] != card["i"]]
        if before > 0 and not ch["hand"] and has(ch, "连营"):
            self.draw(who, 1)
            self.say(f"◆ 连营　{'你' if who == 'you' else '我'}失去最后手牌,摸1张")

    def hurt(self, who, dmg, src=None, card=None, element=None, _chain_pass=False):
        st = self.st
        ch = st[who]
        if armor(ch) == "白银狮子" and dmg > 1:
            self.say(f"◆ 白银狮子　伤害从 {dmg} 点改为 1 点")
            dmg = 1
        if element == "fire" and armor(ch) == "藤甲" and not (src and wep(st[src]) == "青釭剑"):
            dmg += 1
            self.say("◆ 藤甲　受到火焰伤害 +1")
        hp_before = ch["hp"]
        ch["hp"] -= dmg
        self.say(f"◆ 伤害　{'你' if who == 'you' else '我'} -{dmg}({element or '普通'}),剩 {max(ch['hp'],0)}/{ch['maxhp']}")
        if dmg >= 1 and not _chain_pass:
            extra = f"（{card['n']}）" if card else ""
            if dmg >= 2:
                self._flavor("me_big_hit" if who == "you" else "you_big_hit", extra)
            else:
                self._flavor("me_hit" if who == "you" else "you_hit", extra)
        h = ch["hero"]
        local_pends = []
        if h:
            for _i in range(dmg):
                s2_dispatch(self, who, "on_damaged", SkillAPI(self, who), 1, src, card, element)
                if st.get("over"):
                    return
            if has(ch, "反馈") and src and (st[src]["hand"] or st[src]["equip"]):
                sc = st[src]
                if who == "you":
                    opts = self._build_pick_opts(src)
                    if opts:
                        local_pends.append({"t": "pick_card", "kind": "fankui", "src": src})
                        line = "　".join(f"{num}={lab}" for num, _, _, lab in opts)
                        self.say(f"◆ 反馈　选择获得对方一张: {line} (回显示的编号)")
                else:
                    eq = list(sc["equip"].values())
                    picked = None
                    if eq:
                        picked = random.choice(eq)
                    elif sc["hand"]:
                        best = sorted(sc["hand"], key=lambda x: 0 if x["n"] in ("桃", "无懈可击", "杀", "闪") else 1)
                        picked = best[0]
                    if picked:
                        self._steal(src, picked, who)
                        self.say(f"◆ 反馈　{'你' if who == 'you' else '我'}获得 {picked['s']}{picked['r']}{picked['n']}")
            if has(ch, "刚烈") and src:
                j = self.judge(who, "刚烈")
                if j["i"] != -1 and j["s"] != "♥":
                    sc = st[src]
                    if len(sc["hand"]) >= 2:
                        if src == "you":
                            local_pends.append({"t": "ganglie_pick", "dmg_src": src})
                            self.say("◆ 刚烈　你要弃2张手牌(回2个序号),或回0改为受1点伤害")
                        else:
                            cands = sorted(sc["hand"], key=lambda c: 0 if c["n"] not in ("桃", "无懈可击", "杀", "闪", "酒", "火杀", "雷杀") else 1)
                            for c in cands[:2]:
                                self._discard(src, c)
                            self.say("◆ 刚烈　非红桃,来源弃2张手牌")
                    else:
                        self.say("◆ 刚烈　非红桃,来源手牌不足,受1点")
                        self.hurt(src, 1)
            if has(ch, "奸雄") and card:
                st["discard"] = [x for x in st["discard"] if x["i"] != card["i"]]
                ch["hand"].append(card)
                self.say(f"◆ 奸雄　{'你' if who == 'you' else '我'}获得 {card['s']}{card['r']}{card['n']}")
                self.draw(who, 1)
                self.say(f"◆ 奸雄　{'你' if who == 'you' else '我'}再摸1张")
            if has(ch, "遗计"):
                n_draw = 2 * dmg
                got = self.draw(who, n_draw)
                if got:
                    cards_str = " ".join(f"{g['s']}{g['r']}{g['n']}" for g in got)
                    if dmg > 1:
                        self.say(f"◆ 遗计　受到{dmg}点伤害,触发{dmg}次,共摸{len(got)}张: {cards_str}")
                    else:
                        self.say(f"◆ 遗计　{'你' if who == 'you' else '我'}摸2张: {cards_str}")
                else:
                    self.say(f"◆ 遗计　{'你' if who == 'you' else '我'}摸2张: 牌堆空")
        if src:
            src_ch = st[src]
            s2_dispatch(self, src, "on_damage_dealt", SkillAPI(self, src), who, dmg, card, element)
            if st.get("over"):
                return
            if has(src_ch, "狂骨") and distance(src_ch, ch) <= 1:
                if src == "you":
                    local_pends.append({"t": "kuanggu"})
                    self.say("◆ 狂骨　1=回复1点体力 2=摸一张牌")
                else:
                    if src_ch["hp"] < src_ch["maxhp"]:
                        src_ch["hp"] += 1
                        self.say("◆ 狂骨　我回复1点体力")
                        self._check_jieyin()
                    else:
                        self.draw(src, 1)
                        self.say("◆ 狂骨　我满血,摸1张")
            if has(src_ch, "利驭") and card and card["n"] in ("杀", "火杀", "雷杀"):
                self.say("◆ 利驭　触发")
                tgt = None
                wc = st[who]
                if wc["equip"]:
                    tgt = random.choice(list(wc["equip"].values()))
                elif wc["hand"]:
                    best = sorted(wc["hand"], key=lambda x: 0 if x["n"] in ("桃", "无懈可击", "杀", "闪") else 1)
                    tgt = best[0]
                if tgt:
                    self._steal(who, tgt, src)
                    self.say(f"◆ 利驭　{'你' if src == 'you' else '我'}获得 {tgt['s']}{tgt['r']}{tgt['n']}")
                    self.draw(who, 1)
                    self.say(f"◆ 利驭　{'你' if who == 'you' else '我'}摸1张")
        if element and not _chain_pass:
            opp = other(who)
            if ch.get("chained") and st[opp].get("chained"):
                self.say(f"◆ 铁索连环　{'你' if who == 'you' else '我'}受到属性伤害,传导给{'你' if opp == 'you' else '我'}")
                ch["chained"] = False
                st[opp]["chained"] = False
                self.hurt(opp, dmg, src, element=element, _chain_pass=True)
        if local_pends:
            st["pending"] = local_pends[0]
            st["pending_after"] = local_pends[1:]
        if ch["hp"] <= 0:
            if hp_before > 0:
                s2_dispatch(self, who, "on_enter_dying", SkillAPI(self, who))
                if st.get("over"):
                    return
            if not st.get(f"_flavor_dying_{who}"):
                st[f"_flavor_dying_{who}"] = True
                self._flavor("me_dying" if who == "me" else "you_dying")
            self.dying(who)

    def _try_luoyi(self, src, dst):
        ch = self.st[src]
        if not has(ch, "裸衣"):
            return False
        if not ch["hand"]:
            return False
        if self.st["over"]:
            return False
        if src == "you":
            self.st["pending"] = {"t": "luoyi_opt", "dst": dst}
            self.say("◆ 裸衣　可弃一张手牌造成1点额外伤害,1=发动 0=放弃")
            return True
        else:
            cands = sorted(ch["hand"], key=lambda c: 0 if c["n"] not in ("桃", "杀", "闪", "无懈可击") else 1)
            if not cands:
                return False
            c = cands[0]
            self._hand_out(src, c)
            self.st["discard"].append(c)
            self.say(f"◆ 裸衣　我弃 {c['s']}{c['r']}{c['n']},追加1点伤害")
            self.hurt(dst, 1, src)
            return False

    def dying(self, who):
        while True:
            ch = self.st[who]
            if ch["hp"] > 0:
                break
            if who == "me":
                if not self._ai_tao():
                    self.st["over"] = "you"
                    self.say("◆ 结算　我阵亡,你赢了")
                    self._flavor("you_win")
                    return
                continue
            cands = [c for c in ch["hand"] if c["n"] in ("桃", "酒") or (has(ch, "急救") and c["s"] in ("♥", "♦") and self.st["turn"] != "you")]
            can_jiushi = has(ch, "酒诗") and not self.st.get("flipped_you")
            if not cands and not can_jiushi:
                self.st["over"] = "me"
                self.say("◆ 结算　你阵亡,我赢了")
                self._flavor("me_win")
                return
            self.st["pending"] = {"t": "dying"}
            return

    def _ai_tao(self):
        ch = self.st["me"]
        for c in list(ch["hand"]):
            if c["n"] == "桃":
                self._hand_out("me", c)
                self.st["discard"].append(c)
                ch["hp"] += 1
                self.say(f"◆ 救援　我出 {c['s']}{c['r']} 桃,回到 {ch['hp']}")
                self._flavor("me_heal")
                self._check_jieyin()
                self._yajiao_ai()
                return True
        if has(ch, "酒诗") and not self.st.get("flipped_me"):
            self.st["flipped_me"] = True
            ch["hp"] += 1
            self.say(f"◆ 酒诗　我翻面,视为使用一张酒,回到 {ch['hp']}")
            self._flavor("me_heal")
            self._check_jieyin()
            return True
        if has(ch, "急救") and self.st["turn"] != "me":
            for c in list(ch["hand"]):
                if c["s"] in ("♥", "♦") and c["n"] not in ("桃", "酒"):
                    self._hand_out("me", c)
                    self.st["discard"].append(c)
                    ch["hp"] += 1
                    self.say(f"◆ 急救　我出 {c['s']}{c['r']}{c['n']} 当桃,回到 {ch['hp']}")
                    self._flavor("me_heal")
                    self._check_jieyin()
                    return True
        for c in list(ch["hand"]):
            if c["n"] == "酒":
                self._hand_out("me", c)
                self.st["discard"].append(c)
                ch["hp"] += 1
                self.say(f"◆ 救援　我出 {c['s']}{c['r']} 酒,回到 {ch['hp']}")
                self._flavor("me_heal")
                self._check_jieyin()
                self._yajiao_ai()
                return True
        return False

    def _all_cards(self, who):
        ch = self.st[who]
        return list(ch["hand"]) + [v for v in ch["equip"].values()] + list(ch["judge"])

    def _pick_card(self, who, prefer="any", allow_judge=True):
        ch = self.st[who]
        pool = self._all_cards(who) if allow_judge else list(ch["hand"]) + [v for v in ch["equip"].values()]
        if not pool:
            return None
        if allow_judge:
            jd = list(ch["judge"])
            if jd and prefer != "hand":
                return random.choice(jd)
        eq = list(ch["equip"].values())
        if eq and random.random() < 0.55:
            return random.choice(eq)
        if ch["hand"]:
            return random.choice(ch["hand"])
        return random.choice(pool)

    def _pick_equip_first(self, who):
        ch = self.st[who]
        eq = list(ch["equip"].values())
        if eq:
            return random.choice(eq)
        if ch["hand"]:
            return random.choice(ch["hand"])
        if ch["judge"]:
            return random.choice(ch["judge"])
        return None

    def _remove_card(self, who, card):
        ch = self.st[who]
        before = len(ch["hand"])
        ch["hand"] = [c for c in ch["hand"] if c["i"] != card["i"]]
        equip_removed = False
        for k, v in list(ch["equip"].items()):
            if v["i"] == card["i"]:
                del ch["equip"][k]
                equip_removed = True
                s2_dispatch(self, who, "on_equip_lost", SkillAPI(self, who), v)
                if v["n"] == "白银狮子" and ch["hp"] < ch["maxhp"]:
                    ch["hp"] += 1
                    self.say(f"◆ 白银狮子　{'你' if who == 'you' else '我'}回复1点")
                    self._check_jieyin()
                if has(ch, "枭姬"):
                    self.draw(who, 2)
                    self.say(f"◆ 枭姬　{'你' if who == 'you' else '我'}失去装备,摸2张")
        ch["judge"] = [c for c in ch["judge"] if c["i"] != card["i"]]
        if before > 0 and not ch["hand"] and has(ch, "连营"):
            self.draw(who, 1)
            self.say(f"◆ 连营　{'你' if who == 'you' else '我'}失去最后手牌,摸1张")
        if equip_removed and has(ch, "旋风"):
            opp = other(who)
            if who == "you":
                opts = self._build_pick_opts(opp)
                if opts:
                    self.st["pending"] = {"t": "pick_card", "kind": "xuanfeng", "src": opp, "remaining": 2}
                    line = "　".join(f"{num}={lab}" for num, _, _, lab in opts)
                    self.say(f"◆ 旋风　选择弃对方一张(可依次弃至多两张): {line} (回显示的编号)")
                    return
            else:
                for _ in range(2):
                    if self.st.get("pending"):
                        break
                    if not self._all_cards(opp):
                        break
                    tgt = self._pick_card(opp)
                    if not tgt:
                        break
                    self._discard(opp, tgt, allow_pending=False)
                    self.say(f"◆ 旋风　我弃你一张 {tgt['s']}{tgt['r']}{tgt['n']}")
                    if self.st.get("pending"):
                        break

    def _trigger_xuanfeng_discard(self, who):
        st = self.st
        opp = other(who)
        if not self._all_cards(opp):
            return
        if who == "you":
            opts = self._build_pick_opts(opp)
            if opts:
                st["pending"] = {"t": "pick_card", "kind": "xuanfeng", "src": opp, "remaining": 2}
                line = "　".join(f"{num}={lab}" for num, _, _, lab in opts)
                self.say(f"◆ 旋风　弃牌阶段弃≥2张,可依次弃对方至多两张: {line} (回显示的编号)")
        else:
            for _ in range(2):
                if st.get("pending"):
                    break
                if not self._all_cards(opp):
                    break
                tgt = self._pick_card(opp)
                if not tgt:
                    break
                self._discard(opp, tgt, allow_pending=False)
                self.say(f"◆ 旋风　我弃你一张 {tgt['s']}{tgt['r']}{tgt['n']}")
                if st.get("pending"):
                    break

    def _steal(self, who, card, to):
        self._remove_card(who, card)
        self.st[to]["hand"].append(card)

    def _discard(self, who, card, allow_pending=True, is_play=False):
        self._remove_card(who, card)
        self._to_discard(card, allow_pending, is_play=is_play)

    def _target_options(self, who):
        ch = self.st[who]
        opts = []
        if ch["hand"]:
            opts.append(("hand", None, f"手牌随机1张(共{len(ch['hand'])}张)"))
        for k in ("weapon", "armor", "minus", "plus"):
            v = ch["equip"].get(k)
            if v:
                opts.append(("card", v, f"{v['s']}{v['r']} {v['n']}(装备)"))
        for v in ch["judge"]:
            opts.append(("card", v, f"{v['s']}{v['r']} {v['n']}(判定区)"))
        return opts

    def _yinghun_opts(self, who):
        ch = self.st[who]
        hands = [(i + 1, c, f"{i+1} {c['s']}{c['r']}{c['n']}") for i, c in enumerate(ch["hand"])]
        equips = []
        slot_map = [("weapon", "A", "武器"), ("armor", "B", "防具"), ("minus", "C", "-1马"), ("plus", "D", "+1马")]
        for k, letter, name in slot_map:
            v = ch["equip"].get(k)
            if v:
                equips.append((k, letter, v, f"{letter} {v['s']}{v['r']}{v['n']}({name})"))
        return hands, equips

    def _duel_dmg(self):
        return 1

    def _resolve_take(self, n, card):
        if n == "过河拆桥":
            self._discard("me", card)
            self.say(f"◆ 出牌　过河拆桥,拆我 {card['s']}{card['r']}{card['n']}")
        else:
            self._steal("me", card, "you")
            self.say(f"◆ 出牌　顺手牵羊,拿我 {card['s']}{card['r']}{card['n']}")

    def _ai_find_sha(self, check_armor=False):
        me = self.st["me"]
        you = self.st["you"]
        qg = wep(me) == "青釭剑"
        target_armor = armor(you) if check_armor else None
        prefer_red = has(me, "激昂")
        sha_list = [c for c in me["hand"] if c["n"] in ("杀", "火杀", "雷杀")]
        if prefer_red:
            sha_list.sort(key=lambda c: 0 if c["s"] in ("♥", "♦") else 1)
        for c in sha_list:
            if target_armor == "仁王盾" and not qg and c["s"] in ("♠", "♣"):
                continue
            if target_armor == "藤甲" and not qg and c["n"] == "杀":
                continue
            return c, None
        if has(me, "龙胆"):
            for c in me["hand"]:
                if c["n"] == "闪":
                    if target_armor == "仁王盾" and not qg and c["s"] in ("♠", "♣"):
                        continue
                    if target_armor == "藤甲" and not qg:
                        continue
                    return c, "龙胆"
        if has(me, "武圣"):
            for c in me["hand"]:
                if c["s"] in ("♥", "♦") and (c["n"] in WEAPONS or c["n"] in ARMORS or c["n"] in ("-1马", "+1马")):
                    if target_armor == "藤甲" and not qg:
                        continue
                    return c, "武圣"
        return None, None

    def _ai_find_shan(self):
        me = self.st["me"]
        for c in me["hand"]:
            if c["n"] == "闪":
                return c, None
        if has(me, "龙胆"):
            for c in me["hand"]:
                if c["n"] in ("杀", "火杀", "雷杀"):
                    return c, "龙胆"
        if has(me, "倾国"):
            for c in me["hand"]:
                if c["s"] in ("♠", "♣"):
                    return c, "倾国"
        return None, None

    def _yajiao_ai(self):
        me = self.st["me"]
        if not has(me, "涯角"):
            return
        if self.st.get("yajiao_used"):
            return
        if not self.deck:
            return
        self.st["yajiao_used"] = True
        c = self.deck.pop()
        self.say(f"◆ 涯角　展示牌堆顶 {c['s']}{c['r']}{c['n']}")
        if c["n"] in ("杀", "闪", "桃", "酒", "火杀", "雷杀"):
            me["hand"].append(c)
            self.say("◆ 涯角　基本牌,获得之")
        else:
            self.st["discard"].append(c)

    def _ai_shan(self, times=1, ignore_armor=False):
        ch = self.st["me"]
        total = times
        for i in range(times):
            c, desc = self._ai_find_shan()
            if c:
                self._hand_out("me", c)
                self.st["discard"].append(c)
                tag = f"({desc})" if desc else ""
                if total > 1:
                    self.say(f"◆ 应对　我出 {c['s']}{c['r']}{c['n']}{tag} 闪({i+1}/{total})")
                else:
                    self.say(f"◆ 应对　我出 {c['s']}{c['r']}{c['n']}{tag} 闪")
                self._yajiao_ai()
                continue
            if not ignore_armor and armor(ch) == "八卦阵":
                self.say("◆ 八卦阵　我进行判定")
                j = self.judge("me", "八卦阵")
                if j["i"] != -1 and j["s"] in ("♥", "♦"):
                    self.say("◆ 八卦阵　判红,视为出闪")
                    continue
                else:
                    self.say("◆ 八卦阵　判黑,本次没闪")
            if total > 1:
                self.say(f"◆ 结算　我没闪了(已出{i}/{total}张)")
            return False
        return True

    def _ai_sha(self):
        c, desc = self._ai_find_sha()
        if not c:
            return False
        self._hand_out("me", c)
        self.st["discard"].append(c)
        tag = f"({desc})" if desc else ""
        self.say(f"◆ 应对　我出 {c['s']}{c['r']}{c['n']}{tag} 杀")
        if self.st["turn"] != "me":
            self._yajiao_ai()
        return True

    def _ai_tieqi_decide(self, sha_card, element):
        st = self.st
        me, you = st["me"], st["you"]
        j = self.judge("me", "铁骑")
        if j["i"] == -1:
            return
        suit = j["s"]
        you_same = [c for c in you["hand"] if c["s"] == suit]
        dmg = self._calc_dmg(me, you, sha_card)
        if not you_same:
            self.say(f"◆ 铁骑　判定{suit},对手手牌无{suit},无法响应")
            self.hurt("you", dmg, "me", card=sha_card, element=element)
            return
        pending_shan = {"t": "shan", "times": 2 if has(me, "无双") else 1, "dmg": dmg, "qb": armor(you) == "八卦阵" and wep(me) != "青釭剑", "src": "me", "card": sha_card, "element": element, "no_shan": False, "reason": "铁骑"}
        opts_list = [(i, cc) for i, cc in enumerate(you["hand"], 1) if cc["s"] == suit]
        opts_line = "　".join(f"{i}={cc['s']}{cc['r']}{cc['n']}" for i, cc in opts_list)
        st["pending"] = {"t": "tieqi_discard", "suit": suit, "after": pending_shan, "opts_line": opts_line}
        self.say(f"◆ 铁骑　判定{suit},你需弃一张{suit}的牌才能出闪。可弃: {opts_line}；回序号弃牌,0=不弃直接受伤")

    def _ai_sha_attack(self, sha_card, desc=None):
        st = self.st
        me, you = st["me"], st["you"]
        if has(you, "空城") and not you["hand"]:
            self.say("◆ 空城　对方无手牌,杀无效")
            return
        is_black = sha_card["s"] in ("♠", "♣")
        is_attr = sha_card["n"] in ("火杀", "雷杀")
        has_qg = wep(me) == "青釭剑"
        if wep(me) == "雌雄双股剑" and self._gender(me) != self._gender(you):
            self._ai_cixiong_choice("you", "me")
        if armor(you) == "仁王盾" and is_black and not has_qg:
            self.say("◆ 仁王盾　黑杀无效")
            return
        if armor(you) == "藤甲" and not has_qg and not is_attr:
            self.say("◆ 藤甲　普通杀无效")
            return
        _ai_sha_res = s2_dispatch_first(self, "me", "on_sha_target", SkillAPI(self, "me"), sha_card, "you", default=None) or {}
        _ai_no_shan = _ai_sha_res.get("no_shan", False)
        _ai_dmg_bonus = _ai_sha_res.get("dmg_bonus", 0)
        s2_dispatch(self, "you", "on_be_sha_target", SkillAPI(self, "you"), sha_card, "me")
        if has(me, "铁骑"):
            self._ai_tieqi_decide(sha_card, elem_of(sha_card))
            return
        dmg = self._calc_dmg(me, you, sha_card) + _ai_dmg_bonus
        if _ai_no_shan:
            self.say("◆ 烈弓　目标无法出闪")
            self.hurt("you", dmg, "me", card=sha_card, element=elem_of(sha_card))
            return
        st["pending"] = {"t": "shan", "times": 2 if has(me, "无双") else 1, "dmg": dmg, "qb": armor(you) == "八卦阵" and not has_qg, "src": "me", "card": sha_card, "element": elem_of(sha_card), "no_shan": _ai_no_shan, "reason": "烈弓"}

    def _turn(self, who, first_turn=False):
        st = self.st
        if st["over"]:
            return
        guard = 0
        while st.get(f"flipped_{who}"):
            st[f"flipped_{who}"] = False
            self.say(f"◆ 翻面　{'你' if who == 'you' else '我'}翻回正面,跳过本回合")
            _fc = st[who]
            if has(_fc, "酒诗"):
                got = self.draw(who, 1)
                if got:
                    self.say(f"◆ 酒诗　{'你' if who == 'you' else '我'}翻回正面,摸1张({got[0]['s']}{got[0]['r']})")
            who = other(who)
            guard += 1
            if guard > 4 or st["over"]:
                return
        ch = st[who]
        st["turn"] = who
        st["turn_count"] = st.get("turn_count", 0) + 1
        st["sha_used"] = 0
        st["me_sha_used"] = 0
        st["luoyi"] = False
        st["zhiheng_used"] = False
        st["fanjian_used"] = False
        st["qixi_used"] = False
        st["yijue_used"] = False
        st["yajiao_used"] = False
        st["sha_limit_bonus"] = 0
        st["distance_bonus"] = 0
        st["yijue_buff"] = False
        st["jiu"] = False
        st["jiu_used"] = False
        st["pending"] = None
        st["pending_after"] = []
        if st.get("first_player") == who:
            st["qingjian_used_you"] = False
            st["qingjian_used_me"] = False
            st["jieyin_used_you"] = False
            st["jieyin_used_me"] = False
        self.say(f"◆ 回合　{'你' if who == 'you' else '我'}")
        if who == "you" and st["turn_count"] > 2:
            self._flavor("you_turn_start")
        st["jp"] = {"who": who, "skip_play": False, "skip_draw": False, "queue": list(ch["judge"])}
        s2_dispatch(self, who, "on_prepare_phase", SkillAPI(self, who))
        if st["over"]:
            return
        if has(ch, "洛神"):
            self.luoshen(who)
            if st["over"]:
                return
        if has(ch, "英魂") and ch["hp"] < ch["maxhp"]:
            x = ch["maxhp"] - ch["hp"]
            if who == "you":
                st["pending"] = {"t": "yinghun", "x": x}
                self.say(f"◆ 英魂　已损失 {x} 点体力,A=令对手摸1弃{x},0=不发动")
                return
            else:
                opp = st[other(who)]
                self.draw(other(who), 1)
                self.say(f"◆ 英魂　我令你摸1张,请弃 {x} 张")
                hands, equips = self._yinghun_opts("you")
                if hands or equips:
                    need = min(x, len(hands) + len(equips))
                    st["pending"] = {"t": "yinghun_pick", "x": x}
                    parts = [lab for _, _, lab in hands] + [lab for _, _, _, lab in equips]
                    self.say(f"◆ 英魂　请一次回要弃的{need}张(数字/字母空格分隔),可选: " + "　".join(parts))
                    return
                self.say("◆ 英魂　你无牌可弃")
        if has(ch, "观星"):
            top = [self.deck.pop() for _ in range(min(3, len(self.deck)))] if self.deck else []
            if who == "you":
                if top:
                    st["pending"] = {"t": "guanxing", "cards": top}
                    self.say("◆ 观星　牌堆顶:" + "　".join(f"{i}={c['s']}{c['r']}{c['n']}" for i, c in enumerate(top, 1)) + "　回「顶1 2 3」或「顶1 底2 3」或「底1 2 3」")
                    return
            else:
                top.sort(key=lambda c: 0 if c["s"] in ("♠", "♣") else 1)
                for c in reversed(top):
                    self.deck.append(c)
                self.say("◆ 观星　我调整了牌堆顶")
        self._judge_next()

    def _judge_skip(self, n, bad):
        jp = self.st["jp"]
        if n == "乐不思蜀":
            if bad:
                jp["skip_play"] = True
                self.say("◆ 乐　未过红桃,跳过出牌阶段")
            else:
                self.say("◆ 乐　红桃,判定通过")
        else:
            if bad:
                jp["skip_draw"] = True
                self.say("◆ 兵粮　非梅花,跳过摸牌阶段")
            else:
                self.say("◆ 兵粮　梅花,判定通过")

    def _judge_apply_one(self, who, n, orig_card_obj, judge_card):
        st = self.st
        if n == "闪电":
            if judge_card["s"] == "♠" and judge_card["r"] in ("2","3","4","5","6","7","8","9"):
                self.say("◆ 闪电　命中,3点雷电伤害")
                st["discard"].append(orig_card_obj)
                self.hurt(who, 3, element="thunder")
            else:
                self.say("◆ 闪电　未命中,转给对手")
                st[other(who)]["judge"].append(orig_card_obj)
            return False
        if n not in ("乐不思蜀", "兵粮寸断"):
            return False
        bad = (judge_card["s"] != "♥") if n == "乐不思蜀" else (judge_card["s"] != "♣")
        st["discard"].append(orig_card_obj)
        if bad and who == "you" and self._wx_in_hand("you"):
            st["wx"] = {"card": orig_card_obj, "caster": "you", "stack": 0, "judge": True, "label": f"{n}的判定", "apply": (lambda n=n: self._judge_skip(n, True)), "then": self._judge_next}
            self._wx_step("you")
            return True
        self._judge_skip(n, bad)
        return False

    def _judge_next(self):
        st = self.st
        jp = st["jp"]
        who = jp["who"]
        ch = st[who]
        while jp["queue"]:
            c = jp["queue"].pop(0)
            ch["judge"] = [x for x in ch["judge"] if x["i"] != c["i"]]
            n = c["n"]
            j = self.judge(who, n)
            if j["i"] == -1:
                continue
            you = st["you"]
            me = st["me"]
            if has(you, "鬼才") and you["hand"]:
                st["pending"] = {"t": "guicai_opt", "orig": j, "who": who, "why": n, "orig_card_obj": c}
                self.say(f"◆ 鬼才　判定 {j['s']}{j['r']}({n}),可打出手牌替换判定,回手牌序号,0=不改")
                return
            if who == "me" and has(me, "鬼才") and me["hand"]:
                target_suit = None
                need_change = False
                if n == "乐不思蜀" and j["s"] != "♥":
                    target_suit = "♥"
                    need_change = True
                elif n == "兵粮寸断" and j["s"] != "♣":
                    target_suit = "♣"
                    need_change = True
                elif n == "闪电":
                    if j["s"] == "♠" and j["r"] in ("2","3","4","5","6","7","8","9"):
                        need_change = True
                if need_change:
                    candidates = []
                    for cc in me["hand"]:
                        if cc["n"] in ("桃", "无懈可击"):
                            continue
                        if target_suit and cc["s"] == target_suit:
                            candidates.append(cc)
                        elif n == "闪电" and not (cc["s"] == "♠" and cc["r"] in ("2","3","4","5","6","7","8","9")):
                            candidates.append(cc)
                    if candidates:
                        candidates.sort(key=lambda x: 0 if x["n"] not in ("杀", "闪", "火杀", "雷杀", "酒") else 1)
                        replacement = candidates[0]
                        self._hand_out("me", replacement)
                        st["discard"].append(replacement)
                        self.say(f"◆ 鬼才　我用 {replacement['s']}{replacement['r']}{replacement['n']} 替换判定")
                        j = replacement
            if self._judge_apply_one(who, n, c, j):
                return
            if st["over"]:
                return
        self._judge_done()

    def _judge_done(self):
        st = self.st
        jp = st["jp"]
        who = jp["who"]
        ch = st[who]
        if st["over"]:
            return
        if jp["skip_draw"]:
            self._after_draw(who, jp["skip_play"])
            return
        if who == "you":
            opts = [k for k in _names(ch["hero"]) if k in ("突袭",)] if ch["hero"] else []
            if opts:
                st["pending"] = {"t": "drawopt", "opts": opts, "skip_play": jp["skip_play"]}
                self.say("◆ 摸牌阶段　" + "　".join(f"{'AB'[i]}={n}" for i, n in enumerate(opts)) + "　0=正常摸2张")
                return
            self._normal_draw(who)
            self._after_draw(who, jp["skip_play"])
            return
        if ch["hero"]:
            you = st["you"]
            if has(ch, "突袭"):
                if len(you["hand"]) >= 2 and (len(you["hand"]) >= len(ch["hand"]) or you["hp"] <= 2):
                    c = random.choice(you["hand"])
                    self._hand_out("you", c)
                    ch["hand"].append(c)
                    self.say(f"◆ 突袭　我不摸牌,获得你一张 {c['s']}{c['r']}{c['n']}")
                    self.draw(who, 1)
                    self.say("◆ 突袭　我再摸1张")
                    self._after_draw(who, jp["skip_play"])
                    return
        self._normal_draw(who)
        self._after_draw(who, jp["skip_play"])

    def _normal_draw(self, who):
        n = 2
        if has(self.st[who], "英姿"):
            n = 3
            self.say("◆ 英姿　多摸1张")
        for m in s2_dispatch(self, who, "on_modify_draw_count", SkillAPI(self, who)):
            if isinstance(m, int):
                n += m
        self.draw(who, n)
        self.say(f"◆ 摸牌　{'你' if who == 'you' else '我'} +{n}")

    def _after_draw(self, who, skip_play=False):
        if self.st["over"]:
            return
        if who == "me":
            if skip_play:
                self._end("me")
            else:
                self._ai_play()
            return
        if skip_play:
            self._end("you")
            return
        self.st["pending"] = None

    def _end(self, who):
        st = self.st
        ch = st[who]
        over = len(ch["hand"]) - max(ch["hp"], 0)
        if over > 0 and has(ch, "克己") and st["sha_used"] == 0:
            self.say("◆ 克己　本回合未出杀,跳过弃牌阶段")
            over = 0
        discarded_count = 0
        if over > 0:
            if who == "me":
                def _priority(c):
                    n = c["n"]
                    if n == "桃": return 100
                    if n == "无懈可击": return 95
                    if n in ("乐不思蜀", "兵粮寸断"):
                        return 5 if has_judge(st["you"], n) else 85
                    if n == "诸葛连弩": return 88
                    if n in ("杀", "闪", "火杀", "雷杀", "酒"): return 80
                    if n in WEAPONS or n in ARMORS or n in ("-1马", "+1马"): return 70
                    if n in ("无中生有", "顺手牵羊", "过河拆桥", "决斗", "南蛮入侵", "万箭齐发", "火攻", "借刀杀人"): return 60
                    if n in ("五谷丰登", "桃园结义"): return 50
                    if n == "闪电": return 20
                    if n == "铁索连环": return 15
                    return 10
                discarded = []
                for _ in range(over):
                    if ch["hand"]:
                        cands = sorted(ch["hand"], key=_priority)
                        picked = cands[0]
                        self._hand_out("me", picked)
                        self._to_discard(picked, allow_pending=False)
                        discarded.append(picked)
                discarded_count = len(discarded)
                if discarded:
                    self.say("◆ 弃牌　我弃 " + " ".join(f"{c['s']}{c['r']}{c['n']}" for c in discarded))
                else:
                    self.say("◆ 弃牌　我弃到上限")
            else:
                st["pending"] = {"t": "discard", "n": over}
                return
        if discarded_count >= 2 and has(ch, "旋风"):
            self._trigger_xuanfeng_discard(who)
            if st.get("pending"):
                return
        self._end_phase(who)

    def _end_phase(self, who):
        st = self.st
        ch = st[who]
        if has(ch, "据守"):
            if who == "you":
                st["pending"] = {"t": "jushou_opt"}
                self.say("◆ 据守　1=发动(翻面摸4弃1,弃装备则穿戴) 0=放弃")
                return
            else:
                if ch["hp"] <= 2 or len(ch["hand"]) <= 1:
                    self._do_jushou("me")
                    self._ai_jushou_discard()
                    if st.get("over"):
                        return
        s2_dispatch(self, who, "on_end_phase", SkillAPI(self, who))
        if st["over"]:
            return
        if has(ch, "闭月"):
            got = self.draw(who, 1)
            if got:
                self.say(f"◆ 闭月　结束阶段摸1张({got[0]['s']}{got[0]['r']})")
            else:
                self.say("◆ 闭月　牌堆空了")
        st["pending"] = None
        self._turn(other(who))

    def _do_jushou(self, who):
        st = self.st
        st[f"flipped_{who}"] = True
        self.say(f"◆ 据守　{'你' if who == 'you' else '我'}翻面")
        self.draw(who, 4)
        self.say(f"◆ 摸牌　{'你' if who == 'you' else '我'} +4")

    def _has_equip_hand(self, who):
        ch = self.st[who]
        return any(c["n"] in WEAPONS or c["n"] in ARMORS or c["n"] in ("-1马", "+1马") for c in ch["hand"])

    def _equip_card(self, who, card):
        ch = self.st[who]
        n = card["n"]
        if n in WEAPONS:
            slot = "weapon"
        elif n in ARMORS:
            slot = "armor"
        elif n == "-1马":
            slot = "minus"
        elif n == "+1马":
            slot = "plus"
        else:
            self._to_discard(card, allow_pending=False)
            return
        old = ch["equip"].get(slot)
        self._hand_out(who, card)
        ch["equip"][slot] = card
        self.say(f"◆ 装备　{'你' if who == 'you' else '我'}上了 {card['s']}{card['r']} {n}")
        if old:
            if has(ch, "枭姬"):
                self.draw(who, 2)
                self.say(f"◆ 枭姬　{'你' if who == 'you' else '我'}失去装备,摸2张")
            if old["n"] == "白银狮子" and ch["hp"] < ch["maxhp"]:
                ch["hp"] += 1
                self.say(f"◆ 白银狮子　{'你' if who == 'you' else '我'}回复1点")
                self._check_jieyin()
            self._to_discard(old, allow_pending=False)
            if has(ch, "旋风"):
                opp = other(who)
                tgt = self._pick_card(opp)
                if tgt:
                    self._discard(opp, tgt, allow_pending=False)
                    self.say(f"◆ 旋风　{'你' if who == 'you' else '我'}弃对方 {tgt['s']}{tgt['r']}{tgt['n']}")

    def _ai_jushou_discard(self):
        st = self.st
        ch = st["me"]
        can_equip = None
        for c in ch["hand"]:
            n = c["n"]
            if n in WEAPONS:
                cur = ch["equip"].get("weapon")
                if not cur or WEAPON_RANGE.get(n, 1) > WEAPON_RANGE.get(cur["n"], 1):
                    can_equip = c
                    break
            elif n in ARMORS:
                if not ch["equip"].get("armor"):
                    can_equip = c
                    break
            elif n in ("-1马", "+1马"):
                slot = "minus" if n == "-1马" else "plus"
                if not ch["equip"].get(slot):
                    can_equip = c
                    break
        if can_equip:
            self.say(f"◆ 据守　我使用 {can_equip['s']}{can_equip['r']}{can_equip['n']}")
            self._equip_card("me", can_equip)
            return
        def _priority(c):
            n = c["n"]
            if n == "桃": return 100
            if n == "无懈可击": return 95
            if n in ("乐不思蜀", "兵粮寸断"):
                return 5 if has_judge(st["you"], n) else 85
            if n == "诸葛连弩": return 88
            if n in ("杀", "闪", "火杀", "雷杀", "酒"): return 80
            if n in WEAPONS or n in ARMORS or n in ("-1马", "+1马"): return 70
            if n in ("无中生有", "顺手牵羊", "过河拆桥", "决斗", "南蛮入侵", "万箭齐发", "火攻", "借刀杀人"): return 60
            if n in ("五谷丰登", "桃园结义"): return 50
            if n == "闪电": return 20
            if n == "铁索连环": return 15
            return 10
        cands = sorted(ch["hand"], key=_priority)
        if cands:
            picked = cands[0]
            self._hand_out("me", picked)
            self._to_discard(picked, allow_pending=False)
            self.say(f"◆ 据守　我弃 {picked['s']}{picked['r']}{picked['n']}")

    def _ai_play(self):
        st = self.st
        if st.get("_in_ai_play"):
            st["_ai_need_rerun"] = True
            return
        st["_in_ai_play"] = True
        try:
            for _ in range(8):
                st["_ai_need_rerun"] = False
                self._ai_play_impl()
                if not st.get("_ai_need_rerun"):
                    break
                if st.get("over") or st.get("pending") or st.get("turn") != "me":
                    break
        finally:
            st["_in_ai_play"] = False
            st["_ai_need_rerun"] = False

    TRICKS_PRIORITY = {
        "无中生有": 1,
        "顺手牵羊": 2, "过河拆桥": 2,
        "决斗": 3, "南蛮入侵": 3, "万箭齐发": 3,
        "火攻": 4,
        "借刀杀人": 5,
        "五谷丰登": 6,
        "桃园结义": 7,
        "乐不思蜀": 8, "兵粮寸断": 8,
        "闪电": 9,
    }

    def _ai_equip_upgrade_worth(self, new_card, old_card, slot):
        me = self.st["me"]
        you = self.st["you"]
        if slot == "weapon":
            cn = new_card["n"]
            on = old_card["n"]
            if cn == on:
                return False
            sha_cnt = sum(1 for x in me["hand"] if x["n"] in ("杀", "火杀", "雷杀"))
            if cn == "诸葛连弩" and on != "诸葛连弩":
                return sha_cnt >= 2
            if cn == "青釭剑" and on != "青釭剑" and armor(you):
                return True
            if cn == "古锭刀" and on != "古锭刀" and not you["hand"]:
                return True
            if cn == "贯石斧" and on != "贯石斧" and len(me["hand"]) >= 4:
                return True
            if cn == "青龙偃月刀" and on != "青龙偃月刀" and len(me["hand"]) >= 3:
                return True
            if WEAPON_RANGE.get(cn, 1) > WEAPON_RANGE.get(on, 1):
                return True
            return False
        if slot == "armor":
            return ARMOR_RANK.get(new_card["n"], 0) > ARMOR_RANK.get(old_card["n"], 0)
        return False

    def _ai_do_equip(self, card, slot):
        me = self.st["me"]
        old = me["equip"].get(slot)
        if old and not self._ai_equip_upgrade_worth(card, old, slot):
            return False
        self._hand_out("me", card)
        me["equip"][slot] = card
        if old:
            self.say(f"◆ 装备　我换 {card['s']}{card['r']} {card['n']}（替换 {old['n']}）")
            if has(me, "枭姬"):
                self.draw("me", 2)
                self.say("◆ 枭姬　失去装备,摸2张")
            if old["n"] == "白银狮子" and me["hp"] < me["maxhp"]:
                me["hp"] += 1
                self.say("◆ 白银狮子　回复1点")
                self._check_jieyin()
            self._to_discard(old, allow_pending=False)
        else:
            self.say(f"◆ 装备　我上 {card['s']}{card['r']} {card['n']}")
        return True

    def _ai_play_impl(self):
        st = self.st
        me, you = st["me"], st["you"]
        if st["over"] or st.get("pending"):
            return
        self.say(f"◆ 出牌　我行动({len(me['hand'])}张)")
        for c in list(me["hand"]):
            if c["n"] in WEAPONS or c["n"] in ARMORS or c["n"] in ("-1马", "+1马"):
                if c["n"] in WEAPONS:
                    slot = "weapon"
                elif c["n"] in ARMORS:
                    slot = "armor"
                elif c["n"] == "-1马":
                    slot = "minus"
                else:
                    slot = "plus"
                self._ai_do_equip(c, slot)
        if has(me, "制衡") and not st.get("zhiheng_used") and me["hand"]:
            toss = [c for c in me["hand"] if c["n"] != "桃"]
            if toss and len(me["hand"]) >= 4:
                for c in toss:
                    self._discard("me", c)
                if st.get("pending"):
                    return
                self.draw("me", len(toss))
                self.say(f"◆ 制衡　弃 {len(toss)} 摸 {len(toss)}")
                st["zhiheng_used"] = True
        if has(me, "奇袭") and not st.get("qixi_used"):
            blacks = [c for c in me["hand"] if c["s"] in ("♠", "♣")]
            target_count = len(you["hand"]) + len(you["equip"]) + len(you["judge"])
            if blacks and target_count >= 1 and len(me["hand"]) >= 2:
                c = blacks[0]
                self._hand_out("me", c)
                st["discard"].append(c)
                tgt = self._pick_card("you")
                if tgt:
                    self._discard("you", tgt)
                    if st.get("pending"):
                        return
                    self.say(f"◆ 奇袭　我用 {c['s']}{c['r']} 拆你 {tgt['s']}{tgt['r']}{tgt['n']}")
                st["qixi_used"] = True
        if has(me, "青囊") and me["hp"] < me["maxhp"] and me["hand"]:
            worst = None
            for c in me["hand"]:
                if c["n"] in ("闪", "无懈可击"):
                    worst = c
                    break
            if worst is None:
                worst = me["hand"][0]
            self._hand_out("me", worst)
            st["discard"].append(worst)
            me["hp"] += 1
            self.say(f"◆ 青囊　我弃 {worst['s']}{worst['r']}{worst['n']},回复1点,回到 {me['hp']}")
            self._check_jieyin()
        if has(me, "反间") and not st.get("fanjian_used") and len(me["hand"]) >= 2:
            c = me["hand"][0]
            self._hand_out("me", c)
            st["fanjian_used"] = True
            self.say("◆ 反间　我把一张牌扣至手中(花色隐藏),你猜它的花色: 1=♠ 2=♥ 3=♣ 4=♦")
            st["pending"] = {"t": "fanjian_guess", "card": c}
            return
        if has(me, "奇谋") and not st.get("qimou_used") and me["hp"] >= 2:
            sha_card, _ = self._ai_find_sha()
            if sha_card:
                lose = min(me["hp"] - 1, 2)
                need_move = (not in_attack_range(me, you)) or (len(me["hand"]) >= 3)
                if lose > 0 and need_move:
                    st["qimou_used"] = True
                    me["hp"] -= lose
                    st["sha_limit_bonus"] = lose
                    st["distance_bonus"] = lose
                    self.say(f"◆ 奇谋　我失去 {lose} 点体力,本回合杀次数+{lose},距离-{lose}")
        if has(me, "义绝") and not st.get("yijue_used") and me["hand"] and you["hand"]:
            c = me["hand"][0]
            self._hand_out("me", c)
            st["discard"].append(c)
            st["yijue_used"] = True
            st["pending"] = {"t": "yijue_show", "ai_card": c}
            self.say(f"◆ 义绝　我弃 {c['s']}{c['r']},请展示一张手牌(回序号)")
            return
        sha_card, _ = self._ai_find_sha()
        can_use_jiu = False
        if sha_card and not (has(you, "空城") and not you["hand"]):
            has_jiu = any(c["n"] == "酒" for c in me["hand"])
            if has_jiu:
                sha_blocked = False
                if armor(you) == "仁王盾" and sha_card["s"] in ("♠", "♣") and wep(me) != "青釭剑":
                    sha_blocked = True
                if armor(you) == "藤甲" and sha_card["n"] == "杀" and wep(me) != "青釭剑":
                    sha_blocked = True
                in_range = distance(me, you) - st.get("distance_bonus", 0) <= attack_range(me)
                if not sha_blocked and in_range:
                    sha_cnt = sum(1 for x in me["hand"] if x["n"] in ("杀", "火杀", "雷杀"))
                    if you["hp"] <= 2 and len(you["hand"]) <= 2:
                        can_use_jiu = True
                    elif me["hp"] <= 2 and you["hp"] <= 3:
                        can_use_jiu = True
                    elif you["hp"] <= 3 and me["hp"] >= 3 and sha_cnt >= 2:
                        can_use_jiu = True
        if can_use_jiu:
            for c in list(me["hand"]):
                if c["n"] == "酒":
                    self._hand_out("me", c)
                    st["discard"].append(c)
                    st["jiu"] = True
                    st["jiu_used"] = True
                    self.say("◆ 出牌　我使用酒,下张杀+1伤害")
                    break
        if has(me, "酒诗") and not st.get("jiu") and not st.get("jiu_used") and not st.get("flipped_me"):
            _js_sha, _ = self._ai_find_sha()
            if _js_sha and you["hp"] <= 1:
                st["flipped_me"] = True
                st["jiu"] = True
                st["jiu_used"] = True
                self.say("◆ 酒诗　我翻面，视为使用酒")
        if has(me, "苦肉") and me["hp"] >= 2 and len(me["hand"]) <= 2:
            me["hp"] -= 1
            got = self.draw("me", 2)
            self.say("◆ 苦肉　我失1血摸2张:" + " ".join(f"{g['s']}{g['r']}{g['n']}" for g in got))
            if me["hp"] <= 0:
                self.dying("me")
                return
        for c in list(me["hand"]):
            if c["n"] == "无中生有":
                self._hand_out("me", c)
                st["discard"].append(c)
                self._trick(c, "me", lambda c=c: self._apply_ai(c))
                if st["pending"] or st["over"] or st["turn"] != "me":
                    return
        if me["hp"] < me["maxhp"] and me["hp"] > 1:
            for c in list(me["hand"]):
                if c["n"] == "桃":
                    self._hand_out("me", c)
                    st["discard"].append(c)
                    me["hp"] += 1
                    self.say("◆ 出牌　我吃桃,+1血")
                    self._flavor("me_heal")
                    self._check_jieyin()
                    break
        if sha_card and not (has(you, "空城") and not you["hand"]):
            needs_disarm = False
            if armor(you) and wep(me) != "青釭剑":
                sha_blocked = False
                if armor(you) == "仁王盾" and sha_card["s"] in ("♠", "♣"):
                    sha_blocked = True
                if armor(you) == "藤甲" and sha_card["n"] == "杀":
                    sha_blocked = True
                if armor(you) == "八卦阵":
                    sha_blocked = True
                if sha_blocked:
                    needs_disarm = True
            if len(you["hand"]) >= 3 and len(you["equip"]) >= 1:
                needs_disarm = True
            if needs_disarm:
                for cn in ("过河拆桥", "顺手牵羊"):
                    target_c = next((c for c in me["hand"] if c["n"] == cn), None)
                    if not target_c:
                        continue
                    if cn == "顺手牵羊" and distance(me, you) > 1 and not has(me, "奇才"):
                        continue
                    if not self._target_options("you"):
                        continue
                    self._hand_out("me", target_c)
                    st["discard"].append(target_c)
                    self._flavor("me_trick", f"（{cn}）")
                    self._trick(target_c, "me", lambda c=target_c: self._apply_ai(c))
                    if st["pending"] or st["over"] or st["turn"] != "me":
                        return
                    break
        limit = 99 if (wep(me) == "诸葛连弩" or has(me, "咆哮")) else (1 + st.get("sha_limit_bonus", 0))
        liyong_now = has(me, "厉勇") and st.get("liyong_me", False)
        while st.get("me_sha_used", 0) < limit:
            if has(you, "空城") and not you["hand"]:
                break
            if not liyong_now:
                if distance(me, you) - st.get("distance_bonus", 0) > attack_range(me):
                    break
            c, desc = self._ai_find_sha(check_armor=True)
            if not c:
                break
            self._hand_out("me", c)
            st["discard"].append(c)
            st["me_sha_used"] = st.get("me_sha_used", 0) + 1
            tag = f"({desc})" if desc else ""
            self.say(f"◆ 出牌　我出 {c['s']}{c['r']}{c['n']}{tag}")
            self._flavor("me_sha", f"（{c['n']}）")
            is_black = c["s"] in ("♠", "♣")
            is_attr = c["n"] in ("火杀", "雷杀")
            has_qg = wep(me) == "青釭剑"
            _ai_sha_res = s2_dispatch_first(self, "me", "on_sha_target", SkillAPI(self, "me"), c, "you", default=None) or {}
            _ai_no_shan = _ai_sha_res.get("no_shan", False)
            _ai_dmg_bonus = _ai_sha_res.get("dmg_bonus", 0)
            s2_dispatch(self, "you", "on_be_sha_target", SkillAPI(self, "you"), c, "me")
            if liyong_now:
                liyong_now = False
                st["liyong_me"] = False
                if armor(you) == "仁王盾" and is_black and not has_qg:
                    self.say("◆ 仁王盾　黑杀无效")
                    continue
                if armor(you) == "藤甲" and not has_qg and not is_attr:
                    self.say("◆ 藤甲　普通杀无效")
                    continue
                dmg = self._calc_dmg(me, you, c) + (1 if st.get("yijue_buff") else 0) + 1 + _ai_dmg_bonus
                self.say("◆ 厉勇　无视距离,伤害+1,目标不可响应")
                self.hurt("you", dmg, "me", card=c, element=elem_of(c))
                if st["pending"]:
                    return
                self._try_luoyi("me", "you")
                if st["over"] or st["pending"]:
                    return
                continue
            if has(me, "鞬出"):
                tgt = self._pick_card("you", allow_judge=False)
                if tgt:
                    self._discard("you", tgt)
                    if st.get("pending"):
                        return
                    self.say(f"◆ 鞬出　我弃你 {tgt['s']}{tgt['r']}{tgt['n']}")
                    if tgt["n"] not in ("杀", "闪", "桃", "酒", "火杀", "雷杀"):
                        self.say("◆ 鞬出　非基本牌,你不能出闪")
                        dmg = self._calc_dmg(me, you, c) + (1 if st.get("yijue_buff") else 0) + _ai_dmg_bonus
                        self.hurt("you", dmg, "me", card=c, element=elem_of(c))
                        if st["pending"]:
                            return
                        self._try_luoyi("me", "you")
                        self.draw("me", 1)
                        if st["over"] or st["pending"]:
                            return
                        continue
                    self.draw("me", 1)
            if armor(you) == "仁王盾" and is_black and not has_qg:
                self.say("◆ 仁王盾　黑杀无效")
                continue
            if armor(you) == "藤甲" and not has_qg and not is_attr:
                self.say("◆ 藤甲　普通杀无效")
                continue
            if has(me, "铁骑"):
                self._ai_tieqi_decide(c, elem_of(c))
                if st.get("pending") or st["over"]:
                    return
                continue
            dmg = self._calc_dmg(me, you, c) + (1 if st.get("yijue_buff") else 0) + _ai_dmg_bonus
            is_cx = wep(me) == "雌雄双股剑" and self._gender(me) != self._gender(you)
            if _ai_no_shan and not is_cx:
                self.say("◆ 烈弓　目标无法出闪")
                self.hurt("you", dmg, "me", card=c, element=elem_of(c))
                if st["pending"]:
                    return
                self._try_luoyi("me", "you")
                if st["over"] or st["pending"]:
                    return
                continue
            pending_shan = {"t": "shan", "times": 2 if has(me, "无双") else 1, "dmg": dmg, "qb": armor(you) == "八卦阵" and not has_qg, "src": "me", "card": c, "element": elem_of(c), "no_shan": _ai_no_shan, "reason": "烈弓"}
            if is_cx:
                st["pending"] = {"t": "cixiong", "after": pending_shan}
                self.say("◆ 雌雄双股剑　你可以弃一张牌,或让我摸一张。回手牌序号=弃,0=让我摸一张")
                return
            st["pending"] = pending_shan
            return
        opp_low_hp = you["hp"] <= 1
        def _trick_priority(c):
            base = self.TRICKS_PRIORITY.get(c["n"], 10)
            if opp_low_hp and c["n"] in ("决斗", "南蛮入侵", "万箭齐发", "火攻"):
                return base - 5
            return base
        sorted_tricks = sorted(
            [c for c in me["hand"] if c["n"] in self.TRICKS_ACTIVE],
            key=_trick_priority
        )
        for c in sorted_tricks:
            if not any(x["i"] == c["i"] for x in me["hand"]):
                continue
            if c["n"] in ("乐不思蜀", "兵粮寸断") and (has_judge(you, c["n"]) or has(you, "谦逊")):
                continue
            if c["n"] == "闪电" and has_judge(me, "闪电"):
                continue
            if c["n"] in ("顺手牵羊", "过河拆桥") and not self._target_options("you"):
                continue
            if c["n"] == "决斗" and has(you, "空城") and not you["hand"]:
                continue
            if c["n"] == "火攻" and not you["hand"]:
                continue
            if c["n"] == "借刀杀人" and not you["equip"].get("weapon"):
                continue
            if c["n"] in ("顺手牵羊", "兵粮寸断") and not has(me, "奇才") and distance(me, you) > 1:
                continue
            if c["n"] == "桃园结义":
                me_need = me["maxhp"] - me["hp"]
                you_need = you["maxhp"] - you["hp"]
                if me_need <= 0 or me_need <= you_need:
                    continue
            self._hand_out("me", c)
            if c["n"] not in ("乐不思蜀", "兵粮寸断", "闪电"):
                st["discard"].append(c)
            self._flavor("me_trick", f"（{c['n']}）")
            self._trick(c, "me", lambda c=c: self._apply_ai(c))
            if st["pending"] or st["over"] or st["turn"] != "me":
                return
        if not st.get("pending"):
            for c in list(me["hand"]):
                if c["n"] == "铁索连环":
                    self._hand_out("me", c)
                    st["discard"].append(c)
                    got = self.draw("me", 1)
                    if got:
                        self.say(f"◆ 重铸　我重铸铁索,摸 {got[0]['s']}{got[0]['r']}{got[0]['n']}")
                    else:
                        self.say("◆ 重铸")
                    st["_in_ai_play"] = False
                    self._ai_play()
                    return
        if st.get("pending"):
            return
        if st.get("_ai_need_rerun"):
            return
        self._end("me")

    TRICKS_ACTIVE = ("无中生有", "过河拆桥", "顺手牵羊", "决斗", "南蛮入侵", "万箭齐发", "桃园结义", "五谷丰登", "借刀杀人", "乐不思蜀", "兵粮寸断", "闪电", "火攻")

    def _wx_in_hand(self, who):
        return [c for c in self.st[who]["hand"] if c["n"] == "无懈可击"]

    def _trick(self, card, caster, apply_fn):
        if has(self.st[caster], "集智") and card["n"] not in ("乐不思蜀", "兵粮寸断", "闪电"):
            self.draw(caster, 1)
            self.say(f"◆ 集智　{'你' if caster == 'you' else '我'}摸1张")
        self.st["wx"] = {"card": card, "caster": caster, "stack": 0, "apply": apply_fn, "label": card["n"]}
        self._wx_step("you" if caster == "me" else "me")

    def _wx_step(self, responder):
        st = self.st
        wx = st["wx"]
        if responder == "you":
            has_wx = bool(self._wx_in_hand("you"))
            has_jw = has(st["you"], "解围") and self._has_equip_hand("you")
            if not has_wx and not has_jw:
                return self._wx_close()
            st["pending"] = {"t": "wuxie"}
            c = wx["card"]
            who = "我" if wx["caster"] == "me" else "你"
            hint = "（解围：也可回装备牌序号）" if has_jw else ""
            if wx.get("judge"):
                self.say(f"◆ 无懈窗口　这次判定对你不利,要出无懈可击作废吗?回序号,0=认了{hint}")
            elif wx["stack"] == 0:
                self.say(f"◆ 无懈窗口　{who}使出的 {c['s']}{c['r']} {wx['label']},要出无懈可击吗?回序号抵消,0=放行{hint}")
            else:
                self.say(f"◆ 无懈窗口　我打出了无懈可击,要再反制回去吗?回序号,0=放行{hint}")
            return
        c = self._ai_wx_choice(wx)
        if not c:
            return self._wx_close()
        self._hand_out("me", c)
        st["discard"].append(c)
        wx["stack"] += 1
        is_jw = c["n"] != "无懈可击"
        if is_jw:
            self.say(f"◆ 解围　我打出 {c['s']}{c['r']}({c['n']}) 当无懈可击,抵消({wx['label']})")
        else:
            if wx["stack"] == 1:
                head = "抵消"
            else:
                head = "再反一次,抵消上一张"
            self.say(f"◆ 无懈可击　我打出 {c['s']}{c['r']},{head}({wx['label']})")
        return self._wx_step("you")

    def _ai_wx_choice(self, wx):
        me, you = self.st["me"], self.st["you"]
        w = self._wx_in_hand("me")
        jw_cards = []
        if has(me, "解围"):
            core_weapons = ("诸葛连弩", "青釭剑", "古锭刀", "贯石斧", "青龙偃月刀", "麒麟弓", "方天画戟", "丈八蛇矛")
            core_armors = ("八卦阵", "仁王盾")
            for c in me["hand"]:
                cn = c["n"]
                if cn in ARMORS:
                    cur = me["equip"].get("armor")
                    if cur and cn not in core_armors and cur["n"] != cn:
                        jw_cards.append(c)
                    elif not cur and cn not in core_armors:
                        jw_cards.append(c)
                elif cn in WEAPONS:
                    cur = me["equip"].get("weapon")
                    if cn in core_weapons:
                        continue
                    if not cur or WEAPON_RANGE.get(cn, 1) <= WEAPON_RANGE.get(cur["n"], 1):
                        jw_cards.append(c)
                elif cn in ("-1马", "+1马"):
                    slot = "minus" if cn == "-1马" else "plus"
                    if slot in me["equip"]:
                        jw_cards.append(c)
        if not w and not jw_cards:
            return None
        n, caster = wx["label"], wx["caster"]
        if caster == "you":
            if n in ("乐不思蜀", "兵粮寸断", "决斗", "南蛮入侵", "万箭齐发", "借刀杀人"):
                p = 0.85
            elif n in ("顺手牵羊", "过河拆桥", "火攻"):
                p = 0.6
            elif n == "桃园结义":
                p = 0.65 if you["hp"] <= 1 else 0.15
            elif n == "五谷丰登":
                p = 0.5
            elif n == "无中生有":
                p = 0.4
            else:
                p = 0.25
        else:
            p = 0.6
        if me["hp"] <= 1:
            p += 0.1
        if wx["stack"] >= 2:
            p -= 0.45
        if random.random() >= p:
            return None
        if w:
            return w[0]
        if jw_cards:
            jw_cards.sort(key=lambda c: 0 if c["n"] in ("-1马", "+1马") else 1)
            return jw_cards[0]
        return None

    def _wx_close(self):
        st = self.st
        wx = st.get("wx") or {}
        st["wx"] = None
        st["pending"] = None
        is_ai_cast = (wx.get("caster") == "me" and st["turn"] == "me" and not wx.get("then") and not st["over"])
        if wx.get("stack", 0) % 2 == 1:
            self.say(f"◆ 结算　{wx.get('label', '锦囊')} 被无懈可击抵消")
            if is_ai_cast and not st["pending"]:
                self._ai_play()
                return
            then = wx.get("then")
            if then:
                then()
            return
        fn = wx.get("apply")
        if fn:
            fn()
        then = wx.get("then")
        if then:
            then()
            return
        if is_ai_cast and not st["pending"]:
            self._ai_play()

    def handle(self, text):
        text = (text or "").strip()
        st = self.st
        if st["over"]:
            self.reset()
            return self.start()
        p = st["pending"]
        if text in ("详情", "技能", "？", "?"):
            return self.skills_line()
        if p:
            return self._pending(text)
        if st["turn"] != "you":
            self.say("◆ 提示　还没到你")
            return self.out()
        if text in ("0", "过", "结束"):
            self._flavor("you_end_turn")
            self._end("you")
            return self.out()
        if text == "&":
            ch = self.st["you"]
            if wep(ch) != "丈八蛇矛":
                self.say("◆ 提示　你没有装备丈八蛇矛")
                return self.out()
            if len(ch["hand"]) < 2:
                self.say("◆ 提示　至少2张手牌才能用丈八蛇矛")
                return self.out()
            st["pending"] = {"t": "zhangba"}
            self.say("◆ 丈八蛇矛　回两张手牌序号(空格分开)视为使用一张普通杀,0=取消")
            return self.out()
        if text.upper() in ("A", "B", "C", "D", "E") and len(text) == 1:
            self._skill(text.upper())
            return self.out()
        if text.isdigit():
            self._play(int(text))
            return self.out()
        self.say("◆ 提示　数字出牌/字母技能/&=丈八/0结束")
        return self.out()

    def _calc_dmg(self, src, dst, card):
        st = self.st
        dmg = 1
        if st.get("jiu"):
            dmg += 1
            st["jiu"] = False
        if wep(src) == "古锭刀" and not dst["hand"]:
            dmg += 1
            self.say("◆ 古锭刀　目标无手牌,伤害+1")
        return dmg

    def _qilin(self, you):
        st = self.st
        me = st["me"]
        if wep(you) == "麒麟弓" and me["equip"].get("plus") and not st["over"]:
            h = me["equip"].pop("plus")
            st["discard"].append(h)
            self.say("◆ 麒麟弓　弃掉我的+1马")

    def _play(self, idx):
        you = self.st["you"]
        if not (1 <= idx <= len(you["hand"])):
            self.say("◆ 提示　没这张牌")
            return
        c = you["hand"][idx - 1]
        n = c["n"]
        st = self.st
        me = st["me"]
        if n == "无懈可击":
            self.say("◆ 提示　无懈可击只能被动打出")
            return
        if n == "闪":
            if has(you, "龙胆"):
                liyong_now = has(you, "厉勇") and st.get("liyong_you", False)
                limit = 99 if (wep(you) == "诸葛连弩" or has(you, "咆哮")) else (1 + st.get("sha_limit_bonus", 0))
                if st["sha_used"] >= limit:
                    self.say("◆ 提示　这回合的杀用过了")
                    return
                if has(me, "空城") and not me["hand"]:
                    self.say("◆ 提示　对方空城,不能成为杀的目标")
                    return
                if not liyong_now:
                    if distance(you, me) - st.get("distance_bonus", 0) > attack_range(you):
                        self.say(f"◆ 提示　距离 {distance(you, me)} > 攻击范围 {attack_range(you)},杀不到")
                        return
                self._hand_out("you", c)
                st["discard"].append(c)
                st["sha_used"] += 1
                if liyong_now:
                    st["liyong_you"] = False
                    self.say("◆ 厉勇　无视距离,伤害+1,目标不可响应")
                self.say(f"◆ 龙胆　{c['s']}{c['r']} 闪当杀使用")
                virtual = {"i": c["i"], "s": c["s"], "r": c["r"], "n": "杀"}
                self._resolve_sha(virtual, liyong=liyong_now)
                return
            self.say("◆ 提示　闪只能被动打出")
            return
        if n in WEAPONS or n in ARMORS or n in ("-1马", "+1马"):
            if n in WEAPONS:
                slot = "weapon"
            elif n in ARMORS:
                slot = "armor"
            elif n == "-1马":
                slot = "minus"
            else:
                slot = "plus"
            old = you["equip"].get(slot)
            self._hand_out("you", c)
            you["equip"][slot] = c
            self.say(f"◆ 装备　{you['hero']['n']}上了 {c['s']}{c['r']} {n}")
            if old:
                if has(you, "枭姬"):
                    self.draw("you", 2)
                    self.say("◆ 枭姬　失去装备,摸2张")
                if old["n"] == "白银狮子" and you["hp"] < you["maxhp"]:
                    you["hp"] += 1
                    self.say("◆ 白银狮子　回复1点")
                    self._check_jieyin()
                self._to_discard(old)
                if has(you, "旋风"):
                    st["pending"] = {"t": "pick_card", "kind": "xuanfeng", "src": "me", "remaining": 2}
                    opts = self._build_pick_opts("me")
                    line = "　".join(f"{num}={lab}" for num, _, _, lab in opts)
                    self.say(f"◆ 旋风　选择弃对方一张(可依次弃至多两张): {line} (回显示的编号)")
                    return
                if st.get("pending"):
                    return
            if n == "丈八蛇矛":
                self.say("◆ 提示　丈八蛇矛已可用 & 键发动")
            return
        if n == "酒":
            if st.get("jiu_used"):
                self.say("◆ 提示　酒本回合已经用过了")
                return
            self._hand_out("you", c)
            st["discard"].append(c)
            st["jiu"] = True
            st["jiu_used"] = True
            self.say("◆ 出牌　你使用酒,本回合下一张杀伤害+1")
            return
        if n in ("杀", "火杀", "雷杀"):
            liyong_now = has(you, "厉勇") and st.get("liyong_you", False)
            limit = 99 if (wep(you) == "诸葛连弩" or has(you, "咆哮")) else (1 + st.get("sha_limit_bonus", 0))
            if st["sha_used"] >= limit:
                self.say("◆ 提示　这回合的杀用过了")
                return
            if has(me, "空城") and not me["hand"]:
                self.say("◆ 提示　对方空城,不能成为杀的目标")
                return
            if not liyong_now:
                if distance(you, me) - st.get("distance_bonus", 0) > attack_range(you):
                    self.say(f"◆ 提示　距离 {distance(you, me)} > 攻击范围 {attack_range(you)},杀不到")
                    return
            self._hand_out("you", c)
            st["discard"].append(c)
            st["sha_used"] += 1
            if liyong_now:
                st["liyong_you"] = False
                self.say("◆ 厉勇　无视距离,伤害+1,目标不可响应")
            self.say(f"◆ 出牌　你出 {c['s']}{c['r']} {n}")
            self._resolve_sha(c, liyong=liyong_now)
            return
        if n == "桃":
            if you["hp"] >= you["maxhp"]:
                self.say("◆ 提示　满血吃桃浪费")
                return
            self._hand_out("you", c)
            st["discard"].append(c)
            you["hp"] += 1
            self.say(f"◆ 出牌　吃桃,{you['hp']}/{you['maxhp']}")
            self._flavor("you_heal")
            self._check_jieyin()
            return
        if n in self.TRICKS_ACTIVE:
            self._play_trick(c)
            return
        if n == "铁索连环":
            self._hand_out("you", c)
            st["discard"].append(c)
            st["pending"] = {"t": "tiesuo"}
            self.say("◆ 铁索连环　1=横置对手 2=重铸摸牌 0=取消")
            return
        self.say("◆ 提示　这张现在用不了")

    def _play_trick(self, c):
        st = self.st
        you, me = st["you"], st["me"]
        n = c["n"]
        if n in ("顺手牵羊", "兵粮寸断") and not has(you, "奇才") and distance(you, me) > 1:
            self.say(f"◆ 提示　距离 {distance(you, me)} > 1,无法使用{n}")
            return
        if n in ("过河拆桥", "顺手牵羊"):
            if n == "顺手牵羊" and has(me, "谦逊"):
                self.say("◆ 提示　对方有谦逊,顺手无效,请重新选择")
                return
            if not self._target_options("me"):
                self.say(f"◆ 提示　对方没牌,{n}无法使用,请重新选择")
                return
        if n in ("乐不思蜀", "兵粮寸断") and has(me, "谦逊"):
            self.say("◆ 提示　对方有谦逊,不能贴延时,请重新选择")
            return
        if n in ("乐不思蜀", "兵粮寸断") and has_judge(me, n):
            self.say(f"◆ 提示　对方判定区已经有{n}了,请重新选择")
            return
        if n == "闪电":
            if has_judge(you, "闪电"):
                self.say("◆ 提示　你判定区已经有闪电了,请重新选择")
                return
            if has_judge(me, "闪电"):
                self.say("◆ 提示　对方判定区已经有闪电了,请重新选择")
                return
        if n == "决斗" and has(me, "空城") and not me["hand"]:
            self.say("◆ 提示　对方空城,不能决斗,请重新选择")
            return
        if n == "火攻" and not me["hand"]:
            self.say("◆ 提示　对方没手牌,不能火攻,请重新选择")
            return
        if n == "借刀杀人" and not me["equip"].get("weapon"):
            self.say("◆ 提示　对方没有武器,无法使用借刀杀人,请重新选择")
            return
        self._hand_out("you", c)
        if n not in ("乐不思蜀", "兵粮寸断", "闪电"):
            st["discard"].append(c)
        self._flavor("you_trick", f"（{n}）")
        self._trick(c, "you", lambda: self._apply_you(c))

    def _apply_you(self, c):
        st = self.st
        you, me = st["you"], st["me"]
        n = c["n"]
        if n == "无中生有":
            got = self.draw("you", 2)
            self.say("◆ 出牌　无中生有 " + " ".join(f"{g['s']}{g['r']}{g['n']}" for g in got))
            return
        if n in ("过河拆桥", "顺手牵羊"):
            opts = self._target_options("me")
            if len(opts) == 1 and opts[0][0] == "hand":
                self._resolve_take(n, random.choice(me["hand"]))
                return
            st["pending"] = {"t": "target", "n": n, "opts": [[k, v] for k, v, _ in opts], "opts_line": "　".join(f"{i} {lab}" for i, (_, _, lab) in enumerate(opts, 1))}
            return
        if n == "决斗":
            s2_dispatch(self, "you", "on_duel_target", SkillAPI(self, "you"), "me")
            s2_dispatch(self, "me", "on_be_duel_target", SkillAPI(self, "me"), "you")
            self.say("◆ 出牌　决斗,对方先出杀")
            ai_times = 2 if has(you, "无双") else 1
            ok = True
            for _ in range(ai_times):
                if not self._ai_sha():
                    ok = False
                    break
            if not ok:
                dmg = self._duel_dmg()
                self.say(f"◆ 结算　我没杀,吃 {dmg} 点")
                self.hurt("me", dmg, "you", card=c)
                if st["pending"]:
                    return
                if not st["over"]:
                    self._try_luoyi("you", "me")
                if st["pending"]:
                    return
            else:
                need = 2 if has(me, "无双") else 1
                st["pending"] = {"t": "sha", "dmg": 1, "duel": True, "need": need, "ai_times": ai_times, "card": c, "got": 0}
            return
        if n == "火攻":
            show = random.choice(me["hand"])
            self.say(f"◆ 火攻　对方展示 {show['s']}{show['r']}{show['n']}")
            same = [x for x in you["hand"] if x["s"] == show["s"]]
            if not same:
                self.say("◆ 火攻　你没有同花色牌,火攻无效")
                return
            st["pending"] = {"t": "huogong", "suit": show["s"], "card": c}
            self.say(f"◆ 火攻　回同花色({show['s']})手牌序号弃置造成1点火焰伤害,0=算了")
            return
        if n == "南蛮入侵":
            self.say("◆ 出牌　南蛮入侵,我要出杀")
            if armor(me) == "藤甲" and wep(you) != "青釭剑":
                self.say("◆ 藤甲　南蛮入侵无效")
                return
            if not self._ai_sha():
                self.hurt("me", 1, "you", card=c)
            return
        if n == "万箭齐发":
            self.say("◆ 出牌　万箭齐发,我要出闪")
            if armor(me) == "藤甲" and wep(you) != "青釭剑":
                self.say("◆ 藤甲　万箭齐发无效")
                return
            if not self._ai_shan(1):
                self.hurt("me", 1, "you", card=c)
            return
        if n == "桃园结义":
            healed = False
            for w in ("you", "me"):
                if st[w]["hp"] < st[w]["maxhp"]:
                    st[w]["hp"] += 1
                    healed = True
            self.say("◆ 出牌　桃园结义,双方+1血")
            if healed:
                self._check_jieyin()
            return
        if n == "五谷丰登":
            cards = [self.deck.pop() for _ in range(min(2, len(self.deck)))]
            st["reveal"] = cards
            st["pending"] = {"t": "wugu", "cards": cards}
            self.say("◆ 出牌　五谷丰登,亮出2张,回1或2取")
            return
        if n == "借刀杀人":
            if not me["equip"].get("weapon"):
                self.say("◆ 借刀杀人　对方没有武器,无效")
                return
            weapon = me["equip"]["weapon"]
            can_hit = in_attack_range(me, you) and not (has(you, "空城") and not you["hand"])
            sha_c, sha_desc = self._ai_find_sha() if can_hit else (None, None)
            if sha_c:
                self._hand_out("me", sha_c)
                st["discard"].append(sha_c)
                tag = f"({sha_desc})" if sha_desc else ""
                self.say(f"◆ 借刀杀人　我出 {sha_c['s']}{sha_c['r']}{sha_c['n']}{tag} 作为响应")
                self._ai_sha_attack(sha_c)
                return
            del me["equip"]["weapon"]
            you["hand"].append(weapon)
            self.say(f"◆ 借刀杀人　我不出杀,交出武器 {weapon['s']}{weapon['r']}{weapon['n']}")
            return
        if n in ("乐不思蜀", "兵粮寸断"):
            if has_judge(me, n):
                self.say(f"◆ 提示　对方判定区已经有{n}了")
                return
            me["judge"].append(c)
            self.say(f"◆ 出牌　{n} 贴到我判定区")
            return
        if n == "闪电":
            if has_judge(you, "闪电"):
                self.say("◆ 提示　你判定区已经有闪电了")
                return
            you["judge"].append(c)
            self.say("◆ 出牌　闪电贴到自己判定区")
            return

    def _apply_ai(self, c):
        st = self.st
        me, you = st["me"], st["you"]
        n = c["n"]
        if n == "无中生有":
            self.draw("me", 2)
            self.say("◆ 出牌　我无中生有,摸2张")
            return
        if n in ("乐不思蜀", "兵粮寸断"):
            if has_judge(you, n):
                self.say(f"◆ 出牌　{n} 已在你判定区,无效")
                return
            you["judge"].append(c)
            self.say(f"◆ 出牌　{n} 贴到你判定区")
            return
        if n == "南蛮入侵":
            if armor(you) == "藤甲" and wep(me) != "青釭剑":
                self.say("◆ 藤甲　南蛮入侵对你无效")
                return
            st["pending"] = {"t": "sha", "dmg": 1, "card": c}
            self.say("◆ 出牌　南蛮入侵,你要出杀")
            return
        if n == "万箭齐发":
            if armor(you) == "藤甲" and wep(me) != "青釭剑":
                self.say("◆ 藤甲　万箭齐发对你无效")
                return
            st["pending"] = {"t": "shan", "times": 1, "dmg": 1, "qb": armor(you) == "八卦阵" and wep(me) != "青釭剑", "card": c}
            self.say("◆ 出牌　万箭齐发,你要出闪")
            return
        if n == "决斗":
            s2_dispatch(self, "me", "on_duel_target", SkillAPI(self, "me"), "you")
            s2_dispatch(self, "you", "on_be_duel_target", SkillAPI(self, "you"), "me")
            need = 2 if has(me, "无双") else 1
            ai_times = 2 if has(you, "无双") else 1
            st["pending"] = {"t": "sha", "dmg": 1, "duel": True, "need": need, "ai_times": ai_times, "card": c, "got": 0}
            extra = f"(需出{need}张杀)" if need > 1 else ""
            self.say(f"◆ 出牌　决斗,你先出杀{extra}")
            return
        if n == "火攻":
            if not you["hand"]:
                self.say("◆ 火攻　你无手牌,无效")
                return
            st["pending"] = {"t": "huogong_show", "card": c}
            self.say("◆ 火攻　请展示一张手牌,回序号")
            return
        if n == "过河拆桥":
            tgt = self._pick_card("you")
            if tgt:
                self._discard("you", tgt)
                if st.get("pending"):
                    return
                self.say(f"◆ 出牌　过河拆桥,拆你 {tgt['s']}{tgt['r']}{tgt['n']}")
            return
        if n == "顺手牵羊":
            tgt = self._pick_card("you")
            if tgt:
                self._steal("you", tgt, "me")
                self.say(f"◆ 出牌　顺手牵羊,拿走 {tgt['s']}{tgt['r']}{tgt['n']}")
            return
        if n == "桃园结义":
            healed = False
            for w in ("you", "me"):
                if st[w]["hp"] < st[w]["maxhp"]:
                    st[w]["hp"] += 1
                    healed = True
            self.say("◆ 出牌　桃园结义,双方+1血")
            if healed:
                self._check_jieyin()
            return
        if n == "借刀杀人":
            if not you["equip"].get("weapon"):
                self.say("◆ 借刀杀人　对方没有武器,无效")
                return
            w = you["equip"]["weapon"]
            st["pending"] = {"t": "jiedao"}
            self.say(f"◆ 借刀杀人　要求你出杀攻击我,否则交出武器 {w['s']}{w['r']}{w['n']}")
            return
        if n == "五谷丰登":
            cards = [self.deck.pop() for _ in range(min(2, len(self.deck)))]
            if cards and self._wx_in_hand("you"):
                st["pending"] = {"t": "wuxie_wugu_ai", "cards": cards}
                self.say("◆ 无懈窗口　你可以无懈阻止我获得五谷牌,回无懈序号 0=放行")
                return
            got = None
            if cards:
                me["hand"].append(cards[0])
            if len(cards) > 1:
                you["hand"].append(cards[1])
                got = cards[1]
            if got:
                self.say(f"◆ 出牌　五谷丰登,各取1张,你得 {got['s']}{got['r']}{got['n']}")
            else:
                self.say("◆ 出牌　五谷丰登,各取1张")
            return
        if n == "闪电":
            if has_judge(me, "闪电"):
                self.say("◆ 出牌　闪电已在判定区,无效")
                return
            me["judge"].append(c)
            self.say("◆ 出牌　我贴闪电到自己判定区")
            return

    def _resolve_sha(self, card, liyong=False):
        st = self.st
        you, me = st["you"], st["me"]
        if not liyong and not st.get("over"):
            self._flavor("you_sha", f"（{card['n']}）")
        if has(me, "空城") and not me["hand"]:
            self.say("◆ 空城　对方无手牌,杀无效")
            return
        _you_sha_res = s2_dispatch_first(self, "you", "on_sha_target", SkillAPI(self, "you"), card, "me", default=None) or {}
        _you_no_shan = _you_sha_res.get("no_shan", False)
        _you_dmg_bonus = _you_sha_res.get("dmg_bonus", 0)
        s2_dispatch(self, "me", "on_be_sha_target", SkillAPI(self, "me"), card, "you")
        is_black = card["s"] in ("♠", "♣")
        is_attr = card["n"] in ("火杀", "雷杀")
        element = elem_of(card)
        has_qg = wep(you) == "青釭剑"
        if wep(you) == "雌雄双股剑" and not liyong and self._gender(you) != self._gender(me):
            self._ai_cixiong_choice("me", "you")
            if st.get("pending"):
                return
        if has(you, "鞬出") and not liyong:
            tgt = self._pick_card("me", allow_judge=False)
            if tgt:
                self._discard("me", tgt)
                if st.get("pending"):
                    return
                self.say(f"◆ 鞬出　弃我 {tgt['s']}{tgt['r']}{tgt['n']}")
                if tgt["n"] not in ("杀", "闪", "桃", "酒", "火杀", "雷杀"):
                    self.say("◆ 鞬出　非基本牌,我不能出闪")
                    dmg = self._calc_dmg(you, me, card) + (1 if st.get("yijue_buff") else 0) + _you_dmg_bonus
                    self.hurt("me", dmg, "you", card=card, element=element)
                    if st["pending"]:
                        return
                    self._qilin(you)
                    if not st["over"]:
                        self._try_luoyi("you", "me")
                    return
                self.draw("you", 1)
        if armor(me) == "仁王盾" and is_black and not has_qg:
            self.say("◆ 仁王盾　黑杀无效")
            return
        if armor(me) == "藤甲" and not has_qg and not is_attr:
            self.say("◆ 藤甲　普通杀无效")
            return
        if liyong:
            dmg = self._calc_dmg(you, me, card) + (1 if st.get("yijue_buff") else 0) + 1 + _you_dmg_bonus
            self.say("◆ 厉勇　目标不可响应")
            self.hurt("me", dmg, "you", card=card, element=element)
            if st["pending"]:
                return
            self._qilin(you)
            if not st["over"]:
                self._try_luoyi("you", "me")
            return
        times = 2 if has(you, "无双") else 1
        dmg = self._calc_dmg(you, me, card) + (1 if st.get("yijue_buff") else 0) + _you_dmg_bonus
        if _you_no_shan:
            self.say("◆ 烈弓　目标无法出闪")
            self.hurt("me", dmg, "you", card=card, element=element)
            if st["pending"]:
                return
            self._qilin(you)
            if not st["over"]:
                self._try_luoyi("you", "me")
            return
        if has(you, "铁骑"):
            j = self.judge("you", "铁骑")
            if j["i"] != -1:
                suit = j["s"]
                same_suit = [c for c in me["hand"] if c["s"] == suit]
                no_resp = not same_suit
                if no_resp:
                    self.say(f"◆ 铁骑　判定{suit},我手牌无{suit},无法响应")
                    self.hurt("me", dmg, "you", card=card, element=element)
                    if st["pending"]:
                        return
                    self._qilin(you)
                    if not st["over"]:
                        self._try_luoyi("you", "me")
                    return
                can_shan = self._ai_find_shan()[0] is not None or armor(me) == "八卦阵"
                if not can_shan:
                    self.say(f"◆ 铁骑　判定{suit},我无闪也无八卦,无法响应")
                    self.hurt("me", dmg, "you", card=card, element=element)
                    if st["pending"]:
                        return
                    self._qilin(you)
                    if not st["over"]:
                        self._try_luoyi("you", "me")
                    return
                def _tq_priority(cc):
                    nn = cc["n"]
                    if nn == "桃": return 100
                    if nn == "无懈可击": return 95
                    if nn == "闪": return 90
                    if nn in ("杀", "火杀", "雷杀"): return 80
                    if nn in WEAPONS or nn in ARMORS: return 70
                    if nn in ("-1马", "+1马"): return 60
                    if nn in ("乐不思蜀", "兵粮寸断"): return 55
                    return 10
                pick = sorted(same_suit, key=_tq_priority)[0]
                self._hand_out("me", pick)
                st["discard"].append(pick)
                self.say(f"◆ 铁骑　判定{suit},我弃 {pick['s']}{pick['r']}{pick['n']} 换取出闪")
        if self._ai_shan(times, ignore_armor=has_qg):
            self.say("◆ 结算　我出闪,杀没中")
            if has(you, "厉勇"):
                st["liyong_you"] = True
                self.say("◆ 厉勇　你下一张杀无视距离、伤害+1、不可响应")
            if has(you, "猛进"):
                tgt = self._pick_card("me", allow_judge=False)
                if tgt:
                    self._discard("me", tgt)
                    if st.get("pending"):
                        return
                    self.say(f"◆ 猛进　弃我一张 {tgt['s']}{tgt['r']}{tgt['n']}")
            if wep(you) == "青龙偃月刀":
                self.say("◆ 青龙偃月刀　可追加一张杀(回序号继续,0算了)")
                st["pending"] = {"t": "qinglong"}
                return
            if wep(you) == "贯石斧" and len(you["hand"]) >= 2:
                st["pending"] = {"t": "guanshi", "dmg": dmg, "card": card, "element": element}
                self.say("◆ 贯石斧　要弃2张手牌强命中吗?回两张序号,0=算了")
            return
        if wep(you) == "寒冰剑" and not st.get("luoyi") and not st.get("jiu"):
            st["pending"] = {"t": "hanbing", "dmg": dmg, "card": card, "element": element}
            self.say("◆ 寒冰剑　1=防止伤害改为弃对方2张,0=正常伤害")
            return
        self.hurt("me", dmg, "you", card=card, element=element)
        if st["pending"]:
            return
        self._qilin(you)
        if not st["over"]:
            self._try_luoyi("you", "me")

    def _skill(self, letter):
        ch = self.st["you"]
        hero = ch["hero"]
        idx = "ABCDE".index(letter)
        st = self.st
        skills = list(hero["s"])
        if idx >= len(skills):
            self.say("◆ 提示　没这个技能")
            return
        name, timing, key = skills[idx]
        if key == "wusheng":
            if not any(c["s"] in ("♥", "♦") for c in ch["hand"]):
                self.say("◆ 提示　没有红色手牌,武圣不能发动")
                return
            limit = 99 if (wep(ch) == "诸葛连弩" or has(ch, "咆哮")) else (1 + st.get("sha_limit_bonus", 0))
            if st["sha_used"] >= limit:
                self.say("◆ 提示　本回合杀次数已用完")
                return
            st["pending"] = {"t": "wusheng"}
            self.say("◆ 武圣　回一张红色手牌序号当杀使用,0=取消")
            return
        if key == "longdan":
            self.say("◆ 提示　龙胆:出牌阶段直接选闪当杀使用;需要出闪/杀时选杀(含火杀/雷杀)/闪应对")
            return
        if key == "jiushi":
            if st.get("flipped_you"):
                self.say("◆ 提示　你背面朝上，不能发动酒诗主动")
                return
            if st.get("jiu_used"):
                self.say("◆ 提示　本回合酒已经用过了")
                return
            st["flipped_you"] = True
            st["jiu"] = True
            st["jiu_used"] = True
            self.say("◆ 酒诗　你翻面，视为使用一张酒")
            return
        if key == "kurou":
            hp_before = ch["hp"]
            ch["hp"] -= 1
            got = self.draw("you", 2)
            self.say("◆ 苦肉　-1血换2张:" + " ".join(f"{g['s']}{g['r']}{g['n']}" for g in got))
            if ch["hp"] <= 0:
                if hp_before > 0:
                    s2_dispatch(self, "you", "on_enter_dying", SkillAPI(self, "you"))
                    if st.get("over"):
                        return
                self.dying("you")
            return
        if key == "qingnang":
            if not ch["hand"]:
                self.say("◆ 提示　没手牌")
                return
            st["pending"] = {"t": "qingnang"}
            self.say("◆ 青囊　回要弃的手牌序号")
            return
        if key == "guose":
            if not any(c["s"] == "♦" for c in ch["hand"]):
                self.say("◆ 提示　没方块")
                return
            st["pending"] = {"t": "guose"}
            self.say("◆ 国色　回一张方块手牌序号")
            return
        if key == "qixi":
            if not any(c["s"] in ("♠", "♣") for c in ch["hand"]):
                self.say("◆ 提示　没黑色手牌")
                return
            st["pending"] = {"t": "qixi"}
            self.say("◆ 奇袭　回一张黑色手牌序号")
            return
        if key == "zhiheng":
            if st.get("zhiheng_used"):
                self.say("◆ 提示　制衡本回合已用过")
                return
            if not ch["hand"]:
                self.say("◆ 提示　没手牌")
                return
            st["pending"] = {"t": "zhiheng"}
            self.say("◆ 制衡　回要弃的序号(空格分开,可全部)")
            return
        if key == "fanjian":
            if not ch["hand"]:
                self.say("◆ 提示　没手牌")
                return
            st["pending"] = {"t": "fanjian"}
            self.say("◆ 反间　回一张要扣至手中的手牌序号")
            return
        if key == "yinghun":
            if ch["hp"] >= ch["maxhp"]:
                self.say("◆ 提示　未受伤,英魂不能发动")
                return
            x = ch["maxhp"] - ch["hp"]
            st["pending"] = {"t": "yinghun", "x": x}
            self.say(f"◆ 英魂　已损失 {x} 点体力,A=令对手摸1弃{x},0=不发动")
            return
        if key == "qimou":
            if st.get("qimou_used"):
                self.say("◆ 提示　奇谋已用过")
                return
            if ch["hp"] < 2:
                self.say("◆ 提示　体力不足")
                return
            st["pending"] = {"t": "qimou"}
            self.say(f"◆ 奇谋　回要失去的体力数(1~{ch['hp']-1}),0=取消")
            return
        if key == "yijue":
            if st.get("yijue_used"):
                self.say("◆ 提示　义绝本回合已用过")
                return
            if not ch["hand"] or not st["me"]["hand"]:
                self.say("◆ 提示　手牌不足")
                return
            st["pending"] = {"t": "yijue"}
            self.say("◆ 义绝　回要弃置的手牌序号,0=取消")
            return
        if key == "jushou":
            self.say("◆ 提示　据守是结束阶段技能,弃牌阶段后自动询问,无需主动发动")
            return
        if key == "jiewei":
            self.say("◆ 提示　解围在无懈窗口出现时使用,回装备牌序号即可,无需主动发动")
            return
        if key == "liegong":
            self.say("◆ 提示　烈弓是使用杀指定目标后自动触发,无需主动发动")
            return
        if key == "tieqi":
            self.say("◆ 提示　铁骑是使用杀指定目标后自动触发,无需主动发动")
            return
        if key == "chuli":
            self.say("◆ 提示　除疠是进入濒死状态时自动触发,无需主动发动")
            return
        if key == "xuanfeng":
            self.say("◆ 提示　旋风在失去装备或被弃≥2张时自动触发")
            return
        if key == "jiangtang":
            self.say("◆ 提示　激昂在使用/被红色杀、使用/被决斗时自动触发")
            return
        if key == "hunzi":
            self.say("◆ 提示　魂姿在准备阶段体力值为1时自动触发")
            return
        self.say(f"◆ 提示　{name} 现在不是时机({timing})")

    def _pending(self, text):
        st = self.st
        p = st["pending"]
        t = p["t"]
        you, me = st["you"], st["me"]
        if t == "pick":
            tu = (text or "").strip().upper()
            if tu == "A":
                st["pending"] = {"t": "pick_self_name"}
                self.say("◆ 选将　回要指定给自己使用的武将名")
                return self.out()
            if tu == "B":
                st["pending"] = {"t": "pick_opp_name"}
                self.say("◆ 选将　回要指定给敌人使用的武将名")
                return self.out()
            if tu == "0":
                return self._pick_start_custom()
            if text.isdigit() and 1 <= int(text) <= 3:
                return self.pick(int(text) - 1)
            return "◆ 提示　回 1/2/3 或 A/B/0"
        if t == "pick_self_name":
            name = (text or "").strip()
            if name in ("0", "取消"):
                st["pending"] = {"t": "pick"}
                self.say("◆ 选将　取消指定")
                return self.out()
            hero = next((h for h in HEROES if h["n"] == name), None)
            if not hero:
                self.say(f"◆ 提示　找不到武将「{name}」，请重试，回 0 取消")
                return self.out()
            st.setdefault("pick_custom", {})["you"] = hero
            st["pending"] = {"t": "pick"}
            self.say(f"◆ 选将　已指定自己的武将: {hero['n']} ({hero['hp']}血)")
            return self.out()
        if t == "pick_opp_name":
            name = (text or "").strip()
            if name in ("0", "取消"):
                st["pending"] = {"t": "pick"}
                self.say("◆ 选将　取消指定")
                return self.out()
            hero = next((h for h in HEROES if h["n"] == name), None)
            if not hero:
                self.say(f"◆ 提示　找不到武将「{name}」，请重试，回 0 取消")
                return self.out()
            st.setdefault("pick_custom", {})["me"] = hero
            st["pending"] = {"t": "pick"}
            self.say(f"◆ 选将　已指定敌人武将: {hero['n']} ({hero['hp']}血)")
            return self.out()
        if t == "dying":
            if text in ("0", "过", "放弃"):
                st["over"] = "me"
                st["pending"] = None
                self.say("◆ 结算　你阵亡,我赢了")
                self._flavor("me_win")
                return self.out()
            tu = text.upper()
            if len(tu) == 1 and tu in "ABCDE":
                hero = you["hero"]
                ok_jiushi = False
                if hero:
                    idx = "ABCDE".index(tu)
                    if idx < len(hero["s"]) and hero["s"][idx][2] == "jiushi":
                        ok_jiushi = True
                if ok_jiushi:
                    if st.get("flipped_you"):
                        self.say("◆ 提示　你背面朝上,不能发动酒诗")
                        return self.out()
                    st["flipped_you"] = True
                    you["hp"] += 1
                    self.say(f"◆ 酒诗　你翻面,视为使用一张酒,回到 {you['hp']}")
                    self._flavor("you_heal")
                    self._check_jieyin()
                    st["pending"] = None
                    if you["hp"] <= 0:
                        self.dying("you")
                        return self.out()
                    if not st["over"] and st["turn"] == "me":
                        self._ai_play()
                    return self.out()
                self.say("◆ 提示　这张不能当酒")
                return self.out()
            c = self._hand(int(text)) if text.isdigit() else None
            ok = c and (c["n"] in ("桃", "酒") or (has(you, "急救") and c["s"] in ("♥", "♦") and st["turn"] != "you"))
            if not ok:
                self.say("◆ 提示　回桃/酒的序号,或0放弃")
                return self.out()
            self._hand_out("you", c)
            st["discard"].append(c)
            you["hp"] += 1
            self.say(f"◆ 救援　{c['s']}{c['r']} {c['n']},回到 {you['hp']}")
            self._flavor("you_heal")
            self._check_jieyin()
            st["pending"] = None
            if you["hp"] <= 0:
                self.dying("you")
                return self.out()
            if not st["over"] and st["turn"] == "me":
                self._ai_play()
            return self.out()
        if t == "tieqi_discard":
            suit = p["suit"]
            after = p["after"]
            if (text or "").strip() in ("0", "过", "不弃", "放弃"):
                st["pending"] = None
                self.say("◆ 铁骑　不弃牌,直接受伤")
                self.hurt("you", after["dmg"], after["src"], card=after["card"], element=after["element"])
                if st["over"]:
                    return self.out()
                if st["pending"]:
                    return self.out()
                if after["src"] == "me" and not st["over"]:
                    self._try_luoyi("me", "you")
                if st["pending"]:
                    return self.out()
                if st["turn"] == "me":
                    self._ai_play()
                return self.out()
            if not text.isdigit():
                self.say(f"◆ 提示　回{suit}花色的手牌序号弃掉,0=不弃直接受伤")
                return self.out()
            idx = int(text)
            if not (1 <= idx <= len(you["hand"])):
                self.say("◆ 提示　没这张牌")
                return self.out()
            pick = you["hand"][idx - 1]
            if pick["s"] != suit:
                self.say(f"◆ 提示　需弃一张{suit}花色的牌")
                return self.out()
            self._discard("you", pick)
            self.say(f"◆ 铁骑　弃 {pick['s']}{pick['r']}{pick['n']} 换取出闪")
            st["pending"] = after
            return self.out()
        if t == "cixiong":
            after = p["after"]
            if text in ("0", "过"):
                self.draw("me", 1)
                self.say("◆ 雌雄双股剑　你选择让我摸一张")
            else:
                c = self._hand(int(text)) if text.isdigit() else None
                if not c:
                    self.say("◆ 提示　回手牌序号或0")
                    return self.out()
                self._discard("you", c)
                self.say(f"◆ 雌雄双股剑　你弃 {c['s']}{c['r']}{c['n']}")
            if after and after.get("no_shan"):
                st["pending"] = None
                _reason = after.get("reason", "厉勇")
                self.say(f"◆ {_reason}　目标无法出闪")
                self.hurt("you", after.get("dmg", 1), after.get("src"), card=after.get("card"), element=after.get("element"))
                if st.get("pending"):
                    return self.out()
                if not st["over"] and st["turn"] == "me":
                    self._ai_play()
                return self.out()
            st["pending"] = after
            return self.out()
        if t == "pick_card":
            kind = p["kind"]
            src = p["src"]
            opts = self._build_pick_opts(src)
            if not opts:
                st["pending"] = None
                self.say("◆ 提示　对方已无牌")
                if self._pop_pending_after():
                    return self.out()
                self._resume_ai_if_needed()
                return self.out()
            if text.isdigit():
                idx = int(text)
                chosen = None
                for num, kind_key, equip_key, _ in opts:
                    if num == idx:
                        chosen = (kind_key, equip_key)
                        break
                if chosen is None:
                    self.say("◆ 提示　回显示的编号")
                    return self.out()
                kind_key, equip_key = chosen
                if kind_key == "hand":
                    if not st[src]["hand"]:
                        self.say("◆ 提示　对方无手牌")
                        return self.out()
                    card = random.choice(st[src]["hand"])
                else:
                    card = st[src]["equip"].get(equip_key)
                    if not card:
                        self.say("◆ 提示　对方该槽位无装备")
                        return self.out()
                st["pending"] = None
                if kind == "fankui":
                    self._steal(src, card, "you")
                    self.say(f"◆ 反馈　你获得 {card['s']}{card['r']}{card['n']}")
                    if self._pop_pending_after():
                        return self.out()
                    self._resume_ai_if_needed()
                    return self.out()
                else:
                    self._discard(src, card, allow_pending=False)
                    self.say(f"◆ 旋风　弃对方 {card['s']}{card['r']}{card['n']}")
                    if st.get("pending"):
                        return self.out()
                    remaining = p.get("remaining", 1) - 1
                    if remaining > 0:
                        new_opts = self._build_pick_opts(src)
                        if new_opts:
                            st["pending"] = {"t": "pick_card", "kind": "xuanfeng", "src": src, "remaining": remaining}
                            line = "　".join(f"{num}={lab}" for num, _, _, lab in new_opts)
                            self.say(f"◆ 旋风　还可再弃一张: {line} (回显示的编号)")
                            return self.out()
                        else:
                            self.say("◆ 旋风　对方已无牌可弃")
                    if self._pop_pending_after():
                        return self.out()
                    self._resume_ai_if_needed()
                    return self.out()
            self.say("◆ 提示　回显示的编号")
            return self.out()
        if t == "ganglie_pick":
            if text in ("0", "过", "取消"):
                st["pending"] = None
                self.say("◆ 刚烈　放弃弃牌,受1点")
                self.hurt("you", 1)
                if st["pending"]:
                    return self.out()
                if self._pop_pending_after():
                    return self.out()
                self._resume_ai_if_needed()
                return self.out()
            nums = [int(x) for x in text.replace(",", " ").split() if x.isdigit()]
            if len(nums) != 2:
                self.say("◆ 提示　回2张手牌序号或0=受1点")
                return self.out()
            cs = [self._hand(i) for i in nums]
            if any(c is None for c in cs) or len({c["i"] for c in cs}) != 2:
                self.say("◆ 提示　序号不对")
                return self.out()
            for c in cs:
                self._discard("you", c)
            self.say("◆ 刚烈　弃2张手牌")
            st["pending"] = None
            if self._pop_pending_after():
                return self.out()
            self._resume_ai_if_needed()
            return self.out()
        if t == "guicai_opt":
            orig = p["orig"]
            who = p["who"]
            why = p["why"]
            orig_card_obj = p["orig_card_obj"]
            if text.strip() in ("0", "过", ""):
                st["pending"] = None
                self.say("◆ 鬼才　不改判定")
                if self._judge_apply_one(who, why, orig_card_obj, orig):
                    return self.out()
                if not st["over"]:
                    self._judge_next()
                return self.out()
            c = self._hand(int(text)) if text.isdigit() else None
            if not c:
                self.say("◆ 提示　回手牌序号,0=不改")
                return self.out()
            self._hand_out("you", c)
            st["discard"].append(c)
            self.say(f"◆ 鬼才　打出手牌 {c['s']}{c['r']}{c['n']} 替换判定")
            st["pending"] = None
            if self._judge_apply_one(who, why, orig_card_obj, c):
                return self.out()
            if not st["over"]:
                self._judge_next()
            return self.out()
        if t == "luoyi_opt":
            dst = p["dst"]
            st["pending"] = None
            if text.strip() == "1":
                st["pending"] = {"t": "luoyi_pick", "dst": dst}
                self.say("◆ 裸衣　回要弃的手牌序号,0=放弃")
                return self.out()
            else:
                self.say("◆ 裸衣　放弃")
                if not st["over"] and st["turn"] == "me":
                    self._ai_play()
                return self.out()
        if t == "luoyi_pick":
            dst = p["dst"]
            if text in ("0", "过", "取消"):
                st["pending"] = None
                self.say("◆ 裸衣　放弃")
                if not st["over"] and st["turn"] == "me":
                    self._ai_play()
                return self.out()
            c = self._hand(int(text)) if text.isdigit() else None
            if not c:
                self.say("◆ 提示　回手牌序号,0=放弃")
                return self.out()
            self._hand_out("you", c)
            st["discard"].append(c)
            self.say(f"◆ 裸衣　你弃 {c['s']}{c['r']}{c['n']},追加1点伤害")
            st["pending"] = None
            self.hurt(dst, 1, "you")
            if st["pending"]:
                return self.out()
            if not st["over"] and st["turn"] == "me":
                self._ai_play()
            return self.out()
        if t == "qingjian_opt":
            card = p["card"]
            queue = p.get("queue", [])
            st["pending"] = None
            if text.strip() == "1":
                you["hand"].append(card)
                st["qingjian_used_you"] = True
                self.say(f"◆ 清俭　你获得 {card['s']}{card['r']}{card['n']},本清俭次数已用完")
            else:
                if me["hero"] and has(me, "清俭") and not st.get("qingjian_used_me"):
                    if self._valuable_card(card):
                        me["hand"].append(card)
                        st["qingjian_used_me"] = True
                        self.say(f"◆ 清俭　你放弃,我获得 {card['s']}{card['r']}{card['n']}")
                    else:
                        st["discard"].append(card)
                        self.say(f"◆ 清俭　放弃 {card['s']}{card['r']}{card['n']},你可在后续牌中继续选择")
                else:
                    st["discard"].append(card)
                    self.say(f"◆ 清俭　放弃 {card['s']}{card['r']}{card['n']},你可在后续牌中继续选择")
            if queue:
                if st.get("qingjian_used_you"):
                    for qc in queue:
                        if me["hero"] and has(me, "清俭") and not st.get("qingjian_used_me"):
                            if self._valuable_card(qc):
                                me["hand"].append(qc)
                                st["qingjian_used_me"] = True
                                self.say(f"◆ 清俭　我获得 {qc['s']}{qc['r']}{qc['n']}")
                                continue
                        st["discard"].append(qc)
                else:
                    next_card = queue.pop(0)
                    st["pending"] = {"t": "qingjian_opt", "card": next_card, "queue": queue}
                    self.say(f"◆ 清俭　你可以获得 {next_card['s']}{next_card['r']}{next_card['n']},1=获得 0=放弃(放弃不消耗本轮次数)")
                    return self.out()
            if not st["over"] and st["turn"] == "me":
                self._ai_play()
            return self.out()
        if t == "wuxie_wugu":
            rest = p["rest"]
            if text in ("0", "过", "放行"):
                for r in rest:
                    me["hand"].append(r)
                self.say(f"◆ 五谷　我获得剩余 {len(rest)} 张")
                st["pending"] = None
                return self.out()
            c = self._hand(int(text)) if text.isdigit() else None
            if not c or c["n"] != "无懈可击":
                self.say("◆ 提示　回无懈可击序号 0=放行")
                return self.out()
            self._hand_out("you", c)
            st["discard"].append(c)
            self.say("◆ 无懈可击　五谷丰登对我失效")
            for r in rest:
                self._to_discard(r, allow_pending=False)
            st["pending"] = None
            return self.out()
        if t == "wuxie_wugu_ai":
            cards = p["cards"]
            if text in ("0", "过", "放行"):
                got = None
                if cards:
                    me["hand"].append(cards[0])
                if len(cards) > 1:
                    you["hand"].append(cards[1])
                    got = cards[1]
                if got:
                    self.say(f"◆ 五谷　我取1张,你得 {got['s']}{got['r']}{got['n']}")
                else:
                    self.say("◆ 五谷　我取1张")
                st["pending"] = None
                if not st["over"] and st["turn"] == "me":
                    self._ai_play()
                return self.out()
            c = self._hand(int(text)) if text.isdigit() else None
            if not c or c["n"] != "无懈可击":
                self.say("◆ 提示　回无懈可击序号 0=放行")
                return self.out()
            self._hand_out("you", c)
            st["discard"].append(c)
            self.say("◆ 无懈可击　五谷丰登对我失效")
            for r in cards:
                self._to_discard(r, allow_pending=False)
            st["pending"] = None
            if not st["over"] and st["turn"] == "me":
                self._ai_play()
            return self.out()
        if t == "wusheng":
            if text in ("0", "过", "取消"):
                st["pending"] = None
                self.say("◆ 武圣　取消")
                return self.out()
            c = self._hand(int(text)) if text.isdigit() else None
            if not c:
                self.say("◆ 提示　回红色手牌序号,0=取消")
                return self.out()
            if c["s"] not in ("♥", "♦"):
                self.say("◆ 提示　只能选红色手牌")
                return self.out()
            limit = 99 if (wep(you) == "诸葛连弩" or has(you, "咆哮")) else (1 + st.get("sha_limit_bonus", 0))
            if st["sha_used"] >= limit:
                self.say("◆ 提示　本回合杀次数已用完")
                st["pending"] = None
                return self.out()
            if has(me, "空城") and not me["hand"]:
                self.say("◆ 提示　对方空城,不能成为杀的目标")
                st["pending"] = None
                return self.out()
            liyong_now = has(you, "厉勇") and st.get("liyong_you", False)
            if not liyong_now:
                dist = distance(you, me) - st.get("distance_bonus", 0)
                ar = attack_range(you)
                if dist > ar:
                    self.say(f"◆ 提示　距离 {dist} > 攻击范围 {ar}")
                    st["pending"] = None
                    return self.out()
            self._hand_out("you", c)
            st["discard"].append(c)
            st["sha_used"] += 1
            if liyong_now:
                st["liyong_you"] = False
                self.say("◆ 厉勇　无视距离,伤害+1,目标不可响应")
            self.say(f"◆ 武圣　{c['s']}{c['r']} 当杀使用")
            virtual = {"i": c["i"], "s": c["s"], "r": c["r"], "n": "杀"}
            st["pending"] = None
            self._resolve_sha(virtual, liyong=liyong_now)
            return self.out()
        if t == "qimou":
            if text in ("0", "过", "取消"):
                st["pending"] = None
                self.say("◆ 奇谋　取消")
                return self.out()
            if not text.isdigit():
                self.say("◆ 提示　回体力数")
                return self.out()
            x = int(text)
            if x < 1 or x > you["hp"] - 1:
                self.say(f"◆ 提示　回1~{you['hp']-1}")
                return self.out()
            st["qimou_used"] = True
            you["hp"] -= x
            st["sha_limit_bonus"] = x
            st["distance_bonus"] = x
            self.say(f"◆ 奇谋　失去 {x} 点体力,本回合杀次数+{x},距离-{x}")
            st["pending"] = None
            return self.out()
        if t == "kuanggu":
            if text == "1":
                you["hp"] = min(you["hp"] + 1, you["maxhp"])
                self.say(f"◆ 狂骨　回复1点体力,回到 {you['hp']}")
                self._flavor("you_heal")
                self._check_jieyin()
            elif text == "2":
                got = self.draw("you", 1)
                self.say(f"◆ 狂骨　摸1张: {got[0]['s']}{got[0]['r']}{got[0]['n']}")
            else:
                self.say("◆ 提示　1=回血 2=摸牌")
                return self.out()
            st["pending"] = None
            if self._pop_pending_after():
                return self.out()
            if not st["over"] and st["turn"] == "me":
                self._ai_play()
            return self.out()
        if t == "yijue":
            if text in ("0", "过", "取消"):
                st["pending"] = None
                self.say("◆ 义绝　取消")
                return self.out()
            c = self._hand(int(text)) if text.isdigit() else None
            if not c:
                self.say("◆ 提示　回手牌序号")
                return self.out()
            if not me["hand"]:
                self.say("◆ 提示　对方无手牌")
                return self.out()
            self._discard("you", c)
            show = random.choice(me["hand"])
            st["yijue_used"] = True
            if show["s"] in ("♠", "♣"):
                st["yijue_buff"] = True
                self.say(f"◆ 义绝　你弃 {c['s']}{c['r']},对手展示 {show['s']}{show['r']}{show['n']}(黑),本回合你对其杀伤害+1")
            else:
                self._hand_out("me", show)
                you["hand"].append(show)
                self.say(f"◆ 义绝　你弃 {c['s']}{c['r']},对手展示 {show['s']}{show['r']}{show['n']}(红),你获得之")
            st["pending"] = None
            return self.out()
        if t == "yijue_show":
            c = self._hand(int(text)) if text.isdigit() else None
            if not c:
                self.say("◆ 提示　回要展示的手牌序号")
                return self.out()
            ai_card = p["ai_card"]
            self.say(f"◆ 义绝　你展示 {c['s']}{c['r']}{c['n']}")
            if c["s"] in ("♠", "♣"):
                st["yijue_buff"] = True
                self.say(f"◆ 义绝　展示为黑色({c['s']}),本回合他杀你伤害+1")
            else:
                self._hand_out("you", c)
                me["hand"].append(c)
                self.say(f"◆ 义绝　展示为红色({c['s']}),获得 {c['s']}{c['r']}{c['n']}")
            st["pending"] = None
            if not st["over"] and st["turn"] == "me":
                self._ai_play()
            return self.out()
        if t == "yinghun_pick":
            x = p["x"]
            if text in ("0", "过", "停止"):
                st["pending"] = None
                self.say("◆ 英魂　放弃弃牌")
                self._judge_next()
                return self.out()
            hands, equips = self._yinghun_opts("you")
            total = len(hands) + len(equips)
            if total == 0:
                st["pending"] = None
                self.say("◆ 英魂　无牌可弃")
                self._judge_next()
                return self.out()
            need = min(x, total)
            tokens = text.replace(",", " ").replace("，", " ").split()
            picks = []
            seen = set()
            bad = False
            for tok in tokens:
                tup = tok.strip().upper()
                if not tup:
                    continue
                matched = None
                if tup.isdigit():
                    idx = int(tup)
                    for h_idx, c, _lab in hands:
                        if h_idx == idx:
                            matched = c
                            break
                elif tup in ("A", "B", "C", "D"):
                    for _k, l, c, _lab in equips:
                        if l == tup:
                            matched = c
                            break
                else:
                    bad = True
                    break
                if not matched or matched["i"] in seen:
                    bad = True
                    break
                seen.add(matched["i"])
                picks.append(matched)
            if bad or len(picks) != need:
                tips = [lab for _, _, lab in hands] + [lab for _, _, _, lab in equips]
                self.say(f"◆ 提示　英魂需弃 {need} 张,可选: " + "　".join(tips) + "；用空格分隔")
                return self.out()
            for c in picks:
                self._discard("you", c)
                self.say(f"◆ 英魂　弃 {c['s']}{c['r']}{c['n']}")
            st["pending"] = None
            self.say(f"◆ 英魂　共弃 {need} 张")
            self._judge_next()
            return self.out()
        if t == "huogong_show":
            c = self._hand(int(text)) if text.isdigit() else None
            if not c:
                self.say("◆ 提示　回要展示的手牌序号")
                return self.out()
            self.say(f"◆ 火攻　你展示 {c['s']}{c['r']}{c['n']}")
            same = [x for x in me["hand"] if x["s"] == c["s"]]
            st["pending"] = None
            if same:
                x = same[0]
                self._hand_out("me", x)
                st["discard"].append(x)
                self.say(f"◆ 火攻　我弃 {x['s']}{x['r']},造成1点火焰伤害")
                self.hurt("you", 1, "me", card=p.get("card"), element="fire")
            else:
                self.say("◆ 火攻　我没有同花色牌,无效")
            if not st["over"] and st["turn"] == "me":
                self._ai_play()
            return self.out()
        if t == "fanjian_guess":
            suits = ["♠", "♥", "♣", "♦"]
            guess = None
            s = text.strip()
            if s.isdigit() and 1 <= int(s) <= 4:
                guess = suits[int(s) - 1]
            elif s in suits:
                guess = s
            if not guess:
                self.say("◆ 提示　回数字 1=♠ 2=♥ 3=♣ 4=♦ 猜花色")
                return self.out()
            c = p["card"]
            you["hand"].append(c)
            if guess == c["s"]:
                self.say(f"◆ 反间　猜对!花色是 {c['s']},你获得这张牌")
            else:
                self.say(f"◆ 反间　猜错(实际 {c['s']}),你获得这张牌并受1点伤害")
                self.hurt("you", 1, "me")
            st["pending"] = None
            if not st["over"] and st["turn"] == "me":
                self._ai_play()
            return self.out()
        if t == "jiedao":
            weapon = you["equip"].get("weapon")
            if text in ("0", "过", "不出", "不出杀", "算了", "取消"):
                if weapon:
                    del you["equip"]["weapon"]
                    me["hand"].append(weapon)
                    self.say(f"◆ 借刀杀人　交出武器 {weapon['s']}{weapon['r']}{weapon['n']}")
                st["pending"] = None
                if not st["over"] and st["turn"] == "me":
                    self._ai_play()
                return self.out()
            c = self._hand(int(text)) if text.isdigit() else None
            ok = c and (c["n"] in ("杀", "火杀", "雷杀") or (has(you, "龙胆") and c["n"] == "闪") or (has(you, "武圣") and c["s"] in ("♥", "♦")))
            if not ok:
                self.say("◆ 提示　回杀的序号作为响应,或0=不出杀交出武器")
                return self.out()
            if has(me, "空城") and not me["hand"]:
                self.say("◆ 借刀杀人　对方空城,视为无法出杀,交出武器")
                if weapon:
                    del you["equip"]["weapon"]
                    me["hand"].append(weapon)
                    self.say(f"◆ 借刀杀人　交出武器 {weapon['s']}{weapon['r']}{weapon['n']}")
                st["pending"] = None
                if not st["over"] and st["turn"] == "me":
                    self._ai_play()
                return self.out()
            if distance(you, me) - st.get("distance_bonus", 0) > attack_range(you):
                self.say("◆ 借刀杀人　攻击范围不足,视为无法出杀,交出武器")
                if weapon:
                    del you["equip"]["weapon"]
                    me["hand"].append(weapon)
                    self.say(f"◆ 借刀杀人　交出武器 {weapon['s']}{weapon['r']}{weapon['n']}")
                st["pending"] = None
                if not st["over"] and st["turn"] == "me":
                    self._ai_play()
                return self.out()
            self._discard("you", c, is_play=True)
            self.say(f"◆ 借刀杀人　你出 {c['s']}{c['r']} 当杀使用")
            virtual = c if c["n"] in ("杀", "火杀", "雷杀") else {"i": c["i"], "s": c["s"], "r": c["r"], "n": "杀"}
            st["pending"] = None
            self._resolve_sha(virtual)
            if not st["over"] and not st.get("pending") and st["turn"] == "me":
                self._ai_play()
            return self.out()
        if t == "wuxie":
            if text in ("无懈", "无懈可击", "打无懈", "用无懈", "要"):
                idx = [i for i, c in enumerate(self.st["you"]["hand"], 1) if c["n"] == "无懈可击"]
                if not idx and has(you, "解围"):
                    idx = [i for i, c in enumerate(self.st["you"]["hand"], 1)
                           if c["n"] in WEAPONS or c["n"] in ARMORS or c["n"] in ("-1马", "+1马")]
                if not idx:
                    self.say("◆ 提示　你手上没有可当无懈可击的牌")
                    return self.out()
                text = str(idx[0])
            if text in ("0", "过", "放行", "不无懈", "算了"):
                self._wx_close()
                return self.out()
            c = self._hand(int(text)) if text.isdigit() else None
            if not c:
                self.say("◆ 提示　回无懈可击或装备牌序号,0=放行")
                return self.out()
            is_wx = c["n"] == "无懈可击"
            is_equip = c["n"] in WEAPONS or c["n"] in ARMORS or c["n"] in ("-1马", "+1马")
            can_jw = is_equip and has(you, "解围")
            if not (is_wx or can_jw):
                self.say("◆ 提示　这张不能当无懈可击")
                return self.out()
            self._discard("you", c, is_play=True)
            st["wx"]["stack"] += 1
            if can_jw:
                self.say(f"◆ 解围　你打出 {c['s']}{c['r']}({c['n']}) 当无懈可击,抵消上一层")
            else:
                self.say(f"◆ 无懈可击　你打出 {c['s']}{c['r']},抵消上一层")
            self._wx_step("me")
            return self.out()
        if t == "restart":
            if text in ("确认", "是", "好"):
                return "RESTART"
            st["pending"] = None
            self.say("◆ 那就继续")
            return self.out()
        if t == "jushou_opt":
            st["pending"] = None
            if text.strip() in ("1", "是", "发"):
                self._do_jushou("you")
                st["pending"] = {"t": "jushou_discard"}
                self.say("◆ 据守　回要弃的手牌序号(装备牌会改为穿戴)")
                return self.out()
            else:
                self.say("◆ 据守　放弃")
                if not st["over"]:
                    self._turn("me")
                return self.out()
        if t == "jushou_discard":
            if not text.isdigit():
                self.say("◆ 提示　回手牌序号")
                return self.out()
            idx = int(text)
            if not (1 <= idx <= len(you["hand"])):
                self.say("◆ 提示　没这张牌")
                return self.out()
            c = you["hand"][idx - 1]
            n = c["n"]
            st["pending"] = None
            if n in WEAPONS or n in ARMORS or n in ("-1马", "+1马"):
                self.say(f"◆ 据守　穿戴 {c['s']}{c['r']}{n}")
                self._equip_card("you", c)
            else:
                self._discard("you", c)
                self.say(f"◆ 据守　弃 {c['s']}{c['r']}{n}")
            if not st["over"]:
                self._turn("me")
            return self.out()
        if t == "yinghun":
            if text in ("0", "过", "不发动"):
                st["pending"] = None
                self.say("◆ 英魂　不发动")
                self._judge_next()
                return self.out()
            if text.strip().upper() == "A":
                x = p["x"]
                self.draw("me", 1)
                self.say("◆ 英魂　令对手摸1张")
                cnt = 0
                for _ in range(x):
                    if len(me["hand"]) + len(me["equip"]) == 0:
                        break
                    tgt = self._pick_card("me", allow_judge=False)
                    if tgt:
                        self._discard("me", tgt)
                        cnt += 1
                        self.say(f"◆ 英魂　我弃 {tgt['s']}{tgt['r']}{tgt['n']}")
                self.say(f"◆ 英魂　共弃 {cnt} 张")
                st["pending"] = None
                self._judge_next()
                return self.out()
            self.say("◆ 提示　A=令对手摸1弃X,0=不发动")
            return self.out()
        if t == "tiesuo":
            if text in ("0", "过", "取消"):
                st["pending"] = None
                self.say("◆ 铁索连环　取消")
                return self.out()
            if text == "1":
                st["me"]["chained"] = True
                self.say("◆ 铁索连环　横置对手,双方连环")
                st["pending"] = None
                return self.out()
            if text == "2":
                got = self.draw("you", 1)
                if got:
                    self.say(f"◆ 重铸　摸 {got[0]['s']}{got[0]['r']}{got[0]['n']}")
                else:
                    self.say("◆ 重铸")
                st["pending"] = None
                return self.out()
            self.say("◆ 提示　1=横置对手 2=重铸摸牌 0=取消")
            return self.out()
        if t == "zhangba":
            if text in ("0", "过", "取消"):
                st["pending"] = None
                self.say("◆ 丈八蛇矛　取消")
                return self.out()
            nums = [int(x) for x in text.split() if x.isdigit()]
            if len(nums) != 2:
                self.say("◆ 提示　回两张手牌序号(空格分开)")
                return self.out()
            cs = [self._hand(i) for i in nums]
            if any(c is None for c in cs) or len({c["i"] for c in cs}) != 2:
                self.say("◆ 提示　序号不对")
                return self.out()
            for c in cs:
                self._hand_out("you", c)
                st["discard"].append(c)
            st["pending"] = None
            self.say("◆ 丈八蛇矛　两张手牌当普通杀")
            virtual = {"n": "杀", "s": "♠", "r": "A", "i": -1}
            self._resolve_sha(virtual)
            return self.out()
        if t == "huogong":
            if text in ("0", "过"):
                st["pending"] = None
                self.say("◆ 火攻　放弃")
                return self.out()
            c = self._hand(int(text)) if text.isdigit() else None
            if not c or c["s"] != p["suit"]:
                self.say(f"◆ 提示　回同花色({p['suit']})手牌序号")
                return self.out()
            self._discard("you", c)
            self.say("◆ 火攻　造成1点火焰伤害")
            st["pending"] = None
            self.hurt("me", 1, "you", card=p.get("card"), element="fire")
            return self.out()
        if t == "hanbing":
            if text in ("0", "过"):
                st["pending"] = None
                self.say("◆ 寒冰剑　正常伤害")
                self.hurt("me", p["dmg"], "you", card=p.get("card"), element=p.get("element"))
                if st["pending"]:
                    return self.out()
                self._qilin(you)
                if not st["over"]:
                    self._try_luoyi("you", "me")
                return self.out()
            if text == "1":
                st["pending"] = None
                self.say("◆ 寒冰剑　防止伤害,优先弃装备")
                for _ in range(2):
                    tgt = self._pick_equip_first("me")
                    if tgt:
                        self._discard("me", tgt)
                        if st.get("pending"):
                            return self.out()
                    else:
                        break
                return self.out()
            self.say("◆ 提示　1=防止伤害 0=正常伤害")
            return self.out()
        if t == "discard":
            nums = [int(x) for x in text.replace(",", " ").split() if x.isdigit()]
            if len(nums) != p["n"]:
                self.say(f"◆ 提示　要弃 {p['n']} 张")
                return self.out()
            cs = [self._hand(i) for i in nums]
            if any(c is None for c in cs) or len({c["i"] for c in cs}) != len(cs):
                self.say("◆ 提示　序号不对")
                return self.out()
            for c in cs:
                self._discard("you", c)
            self.say("◆ 弃牌　弃 " + " ".join(f"{c['s']}{c['r']}{c['n']}" for c in cs))
            st["pending"] = None
            if len(cs) >= 2 and has(you, "旋风"):
                self._trigger_xuanfeng_discard("you")
                if st.get("pending"):
                    return self.out()
            self._end_phase("you")
            return self.out()
        if t == "zhiheng":
            nums = [int(x) for x in text.replace(",", " ").split() if x.isdigit()]
            cs = [self._hand(i) for i in nums]
            if not cs or any(c is None for c in cs) or len({c["i"] for c in cs}) != len(cs):
                self.say("◆ 提示　序号不对")
                return self.out()
            for c in cs:
                self._discard("you", c)
            got = self.draw("you", len(cs))
            st["zhiheng_used"] = True
            self.say(f"◆ 制衡　弃 {len(cs)} 摸 {len(got)}")
            st["pending"] = None
            return self.out()
        if t == "fanjian":
            c = self._hand(int(text)) if text.isdigit() else None
            if not c:
                self.say("◆ 提示　回手牌序号")
                return self.out()
            self._hand_out("you", c)
            guess = random.choice(SUITS)
            me["hand"].append(c)
            if guess != c["s"]:
                self.say(f"◆ 反间　对手猜 {guess},猜错(实际 {c['s']}),获得这张牌并受1点伤害")
                self.hurt("me", 1, "you")
            else:
                self.say(f"◆ 反间　对手猜 {guess},猜对(实际 {c['s']}),获得这张牌,无伤")
            st["pending"] = None
            return self.out()
        if t == "guanxing":
            raw = (text or "").strip()
            n = len(p["cards"])
            if raw in ("底", "下", "0"):
                self.deck[0:0] = list(p["cards"])
                st["pending"] = None
                self.say("◆ 观星　全部放回牌堆底")
                self._judge_next()
                return self.out()
            tokens = raw.replace("，", " ").replace(",", " ").split()
            top, bottom = [], []
            seen = set()
            current_dir = "top"
            ok = True
            for tok in tokens:
                t_ = tok.strip()
                if not t_:
                    continue
                m = re.match(r"^(顶|底|上|下)?([0-9]{1,2})$", t_)
                if m:
                    dir_word = m.group(1)
                    idx = int(m.group(2))
                    if dir_word in ("顶", "上"):
                        current_dir = "top"
                    elif dir_word in ("底", "下"):
                        current_dir = "bottom"
                    if idx < 1 or idx > n or idx in seen:
                        ok = False
                        break
                    seen.add(idx)
                    card = p["cards"][idx - 1]
                    if current_dir == "top":
                        top.append(card)
                    else:
                        bottom.append(card)
                elif t_ in ("顶", "上"):
                    current_dir = "top"
                elif t_ in ("底", "下"):
                    current_dir = "bottom"
                else:
                    ok = False
                    break
            if not ok or len(seen) != n:
                self.say("◆ 提示　顶1 2 3=全放顶;顶1 底2 3=1顶2和3底;底1 2 3=全放底")
                return self.out()
            if bottom:
                self.deck[0:0] = bottom
            for c in reversed(top):
                self.deck.append(c)
            st["pending"] = None
            self.say("◆ 观星　顺序已定")
            self._judge_next()
            return self.out()
        if t == "guanshi":
            if text in ("0", "过", "算了"):
                st["pending"] = None
                self.say("◆ 贯石斧　算了")
                return self.out()
            nums = [int(x) for x in text.replace(",", " ").split() if x.isdigit()]
            if len(nums) != 2:
                self.say("◆ 提示　要弃2张手牌")
                return self.out()
            cs = [self._hand(i) for i in nums]
            if any(c is None for c in cs) or len({c["i"] for c in cs}) != 2:
                self.say("◆ 提示　序号不对")
                return self.out()
            for c in cs:
                self._discard("you", c)
            st["pending"] = None
            self.say("◆ 贯石斧　弃2张,强制命中")
            self.hurt("me", p.get("dmg", 1), "you", card=p.get("card"), element=p.get("element"))
            if st["pending"]:
                return self.out()
            if not st["over"]:
                self._try_luoyi("you", "me")
            return self.out()
        if t == "shan":
            if p.get("no_shan"):
                st["pending"] = None
                _reason = p.get("reason", "厉勇")
                self.say(f"◆ {_reason}　无法响应")
                self.hurt("you", p.get("dmg", 1), p.get("src"), card=p.get("card"), element=p.get("element"))
                if st["over"]:
                    return self.out()
                if st["pending"]:
                    return self.out()
                if p.get("src") == "me" and not st["over"]:
                    self._try_luoyi("me", "you")
                if st["pending"]:
                    return self.out()
                if st["turn"] == "me":
                    self._ai_play()
                return self.out()
            if p.get("qb"):
                self.say("◆ 提示　你有八卦阵,可回#或八卦进行判定")
            if text in ("0", "过"):
                st["pending"] = None
                self.say("◆ 结算　你没闪")
                self.hurt("you", p.get("dmg", 1), p.get("src"), card=p.get("card"), element=p.get("element"))
                if st["over"]:
                    return self.out()
                if st["pending"]:
                    return self.out()
                if p.get("src") == "me" and not st["over"]:
                    self._try_luoyi("me", "you")
                if st["pending"]:
                    return self.out()
                if st["turn"] == "me":
                    self._ai_play()
                return self.out()
            if text in ("#", "@", "八卦", "八", "卦"):
                if not p.get("qb"):
                    self.say("◆ 提示　本次杀不能再判定八卦阵,请出真闪或回0")
                    return self.out()
                j = self.judge("you", "八卦阵")
                if j["i"] != -1 and j["s"] in ("♥", "♦"):
                    p["times"] -= 1
                    self.say("◆ 八卦阵　判红,视为出闪")
                    if p["times"] <= 0:
                        st["pending"] = None
                        self.say("◆ 结算　闪住了")
                        if p.get("src") == "me" and has(me, "厉勇"):
                            st["liyong_me"] = True
                            self.say("◆ 厉勇　我下一张杀无视距离、伤害+1、不可响应")
                        if st["turn"] == "me":
                            self._ai_play()
                    else:
                        self.say(f"◆ 提示　还需出 {p['times']} 张闪,可回#再判八卦阵,或出真闪")
                else:
                    p["qb"] = False
                    self.say("◆ 八卦阵　判黑,本次杀不能再判定八卦阵,请出真闪或回0")
                return self.out()
            c = self._hand(int(text)) if text.isdigit() else None
            ok = c and (c["n"] == "闪" or (has(you, "龙胆") and c["n"] in ("杀", "火杀", "雷杀")) or (has(you, "倾国") and c["s"] in ("♠", "♣")))
            if not ok:
                self.say("◆ 提示　这张不能当闪")
                return self.out()
            self._discard("you", c, is_play=True)
            self.say(f"◆ 应对　你出 {c['s']}{c['r']} 当闪")
            if has(you, "涯角") and not st.get("yajiao_used") and self.deck:
                st["yajiao_used"] = True
                top = self.deck.pop()
                self.say(f"◆ 涯角　展示牌堆顶 {top['s']}{top['r']}{top['n']}")
                if top["n"] in ("杀", "闪", "桃", "酒", "火杀", "雷杀"):
                    you["hand"].append(top)
                    self.say("◆ 涯角　基本牌,获得之")
                else:
                    st["discard"].append(top)
            p["times"] -= 1
            if p["times"] <= 0:
                st["pending"] = None
                self.say("◆ 结算　闪住了")
                if p.get("src") == "me" and has(me, "厉勇"):
                    st["liyong_me"] = True
                    self.say("◆ 厉勇　我下一张杀无视距离、伤害+1、不可响应")
                if st["turn"] == "me":
                    self._ai_play()
            return self.out()
        if t == "sha":
            duel = p.get("duel")
            if text in ("0", "过"):
                st["pending"] = None
                self.say("◆ 结算　你没杀")
                if duel:
                    dmg = self._duel_dmg()
                    self.hurt("you", dmg, "me", card=p.get("card"))
                    if st["pending"]:
                        return self.out()
                    if not st["over"]:
                        self._try_luoyi("me", "you")
                else:
                    self.hurt("you", p.get("dmg", 1), "me", card=p.get("card"))
                if st["over"]:
                    return self.out()
                if st["pending"]:
                    return self.out()
                if st["turn"] == "me":
                    self._ai_play()
                return self.out()
            c = self._hand(int(text)) if text.isdigit() else None
            ok = c and (c["n"] in ("杀", "火杀", "雷杀") or (has(you, "龙胆") and c["n"] == "闪") or (has(you, "武圣") and c["s"] in ("♥", "♦")))
            if not ok:
                self.say("◆ 提示　这张不能当杀")
                return self.out()
            self._discard("you", c, is_play=True)
            self.say(f"◆ 应对　你出 {c['s']}{c['r']} 当杀")
            if has(you, "涯角") and not st.get("yajiao_used") and self.deck:
                st["yajiao_used"] = True
                top = self.deck.pop()
                self.say(f"◆ 涯角　展示牌堆顶 {top['s']}{top['r']}{top['n']}")
                if top["n"] in ("杀", "闪", "桃", "酒", "火杀", "雷杀"):
                    you["hand"].append(top)
                    self.say("◆ 涯角　基本牌,获得之")
                else:
                    st["discard"].append(top)
            if duel:
                p["got"] = p.get("got", 0) + 1
                need = p.get("need", 1)
                if p["got"] < need:
                    remain = need - p["got"]
                    self.say(f"◆ 决斗　还需再出 {remain} 张杀")
                    return self.out()
                ai_times = p.get("ai_times", 1)
                if not all(self._ai_sha() for _ in range(ai_times)):
                    st["pending"] = None
                    dmg = self._duel_dmg()
                    self.say(f"◆ 结算　我没杀,吃 {dmg} 点")
                    self.hurt("me", dmg, "you", card=p.get("card"))
                    if st["pending"]:
                        return self.out()
                    if not st["over"]:
                        self._try_luoyi("you", "me")
                    if st["pending"]:
                        return self.out()
                    if not st["over"] and st["turn"] == "me":
                        self._ai_play()
                else:
                    p["got"] = 0
                    st["pending"] = p
                    self.say("◆ 决斗　轮到你出杀")
                return self.out()
            st["pending"] = None
            if st["turn"] == "me":
                self._ai_play()
            return self.out()
        if t == "duel":
            if text in ("0", "过"):
                st["pending"] = None
                self.say("◆ 结算　你认输,吃1点")
                self.hurt("you", 1, "me")
                return self.out()
            c = self._hand(int(text)) if text.isdigit() else None
            if not c or c["n"] not in ("杀", "火杀", "雷杀"):
                self.say("◆ 提示　决斗只能回杀的序号")
                return self.out()
            self._discard("you", c, is_play=True)
            if not self._ai_sha():
                st["pending"] = None
                self.say("◆ 结算　我没杀,吃1点")
                self.hurt("me", 1, "you")
                if st["pending"]:
                    return self.out()
                if not st["over"]:
                    self._try_luoyi("you", "me")
                if st["pending"]:
                    return self.out()
                if not st["over"] and st["turn"] == "me":
                    self._ai_play()
            else:
                st["pending"] = {"t": "sha", "dmg": 1, "duel": True, "need": 1, "ai_times": 1, "got": 0}
            return self.out()
        if t == "wugu":
            if text in ("1", "2") and int(text) <= len(p["cards"]):
                c = p["cards"][int(text) - 1]
                you["hand"].append(c)
                rest = [r for r in p["cards"] if r["i"] != c["i"]]
                st["reveal"] = None
                self.say(f"◆ 五谷　你取 {c['s']}{c['r']}{c['n']}")
                if rest:
                    if self._wx_in_hand("you"):
                        st["pending"] = {"t": "wuxie_wugu", "rest": rest}
                        self.say("◆ 无懈窗口　你可以无懈阻止我获得剩余五谷牌,回无懈序号 0=放行")
                        return self.out()
                    for r in rest:
                        me["hand"].append(r)
                    self.say(f"◆ 五谷　我获得剩余 {len(rest)} 张")
                st["pending"] = None
                return self.out()
            self.say("◆ 提示　回1或2")
            return self.out()
        if t == "qingnang":
            c = self._hand(int(text)) if text.isdigit() else None
            if not c:
                self.say("◆ 提示　回手牌序号")
                return self.out()
            self._discard("you", c)
            you["hp"] = min(you["hp"] + 1, you["maxhp"])
            self.say(f"◆ 青囊　弃 {c['s']}{c['r']}{c['n']},回到 {you['hp']}")
            self._flavor("you_heal")
            self._check_jieyin()
            st["pending"] = None
            return self.out()
        if t == "guose":
            c = self._hand(int(text)) if text.isdigit() else None
            if not c or c["s"] != "♦":
                self.say("◆ 提示　回方块序号")
                return self.out()
            if has_judge(me, "乐不思蜀"):
                self.say("◆ 提示　对方判定区已经有乐不思蜀了")
                return self.out()
            self._hand_out("you", c)
            st["pending"] = None
            self._trick(c, "you", lambda c=c: (me["judge"].append(c), self.say("◆ 国色　当乐不思蜀贴给我")))
            return self.out()
        if t == "qixi":
            c = self._hand(int(text)) if text.isdigit() else None
            if not c or c["s"] not in ("♠", "♣"):
                self.say("◆ 提示　回黑色序号")
                return self.out()
            self._hand_out("you", c)
            st["pending"] = None
            self._trick(c, "you", lambda c=c: self._qixi_apply(c))
            return self.out()
        if t == "qinglong":
            c = self._hand(int(text)) if text.isdigit() else None
            if not c or c["n"] not in ("杀", "火杀", "雷杀"):
                st["pending"] = None
                self.say("◆ 青龙偃月刀　没追加")
                return self.out()
            self._hand_out("you", c)
            st["discard"].append(c)
            st["pending"] = None
            self.say("◆ 青龙偃月刀　追一刀")
            self._resolve_sha(c)
            return self.out()
        if t == "drawopt":
            txt = text.strip().upper()
            if txt in ("0", "过"):
                self._normal_draw("you")
                self._after_draw("you", p.get("skip_play", False))
                return self.out()
            if txt == "A" and len(p["opts"]) >= 1:
                n = p["opts"][0]
                if n == "突袭":
                    if me["hand"]:
                        c = random.choice(me["hand"])
                        self._hand_out("me", c)
                        you["hand"].append(c)
                        self.say(f"◆ 突袭　获得对手一张 {c['s']}{c['r']}{c['n']}")
                        self.draw("you", 1)
                        self.say("◆ 突袭　再摸1张")
                    else:
                        self._normal_draw("you")
                self._after_draw("you", p.get("skip_play", False))
                return self.out()
            self.say("◆ 提示　回A或0")
            return self.out()
        if t == "target":
            opts = p["opts"]
            if text.isdigit() and 1 <= int(text) <= len(opts):
                kind, card = opts[int(text) - 1]
                st["pending"] = None
                if kind == "hand":
                    if not me["hand"]:
                        self.say("◆ 提示　我手牌已经没了,换一张")
                        st["pending"] = p
                        return self.out()
                    card = random.choice(me["hand"])
                self._resolve_take(p["n"], card)
                return self.out()
            self.say(f"◆ 提示　回1~{len(opts)}选牌")
            return self.out()
        st["pending"] = None
        return self.out()

    def _qixi_apply(self, c):
        st = self.st
        tgt = self._pick_card("me")
        if not any(x["i"] == c["i"] for x in st["discard"]):
            st["discard"].append(c)
        if tgt:
            self._discard("me", tgt)
            if st.get("pending"):
                return
            self.say(f"◆ 奇袭　拆我 {tgt['s']}{tgt['r']}{tgt['n']}")

    def _hand(self, idx):
        h = self.st["you"]["hand"]
        if 1 <= idx <= len(h):
            return h[idx - 1]
        return None

    def public_summary(self) -> str:
        st = self.st
        you, me = st["you"], st["me"]
        if not (you["hero"] and me["hero"]):
            return ""
        you_name = you["hero"]["n"]
        me_name = me["hero"]["n"]

        def _eq(ch):
            return "、".join(v["n"] for v in ch["equip"].values()) or "无"

        def _jd(ch):
            return "、".join(c["n"] for c in ch["judge"]) or "无"

        def _skills(ch):
            if not ch["hero"]:
                return "无"
            return "、".join(s[0] for s in ch["hero"].get("s", [])) or "无"

        first = st.get("first_player")
        first_name = you_name if first == "you" else (me_name if first == "me" else "?")
        turn_desc = "玩家" if st["turn"] == "you" else "AI"

        chain = []
        if you.get("chained"):
            chain.append(you_name)
        if me.get("chained"):
            chain.append(me_name)
        chain_line = f"铁索横置：{'、'.join(chain)}\n" if chain else ""

        if st["over"]:
            end = f"【已结束】{'玩家' if st['over']=='you' else 'AI'}获胜\n"
        elif st["pending"]:
            end = f"【等待玩家操作：{st['pending']['t']}】\n"
        else:
            end = f"【当前轮到 {turn_desc} 出牌】\n"

        recent = ""
        if self.history:
            recent = "【最近发生】\n" + "\n".join(
                "- " + h.lstrip("◆ ").strip() for h in self.history[-10:]
            ) + "\n"

        return (
            f"【第 {st.get('turn_count', 0)} 回合 · {you_name}(玩家) vs {me_name}(AI) · 先手：{first_name}】\n"
            f"【玩家 {you_name}】{max(you['hp'],0)}/{you['maxhp']} 血 · {len(you['hand'])} 手牌 · "
            f"装备：{_eq(you)} · 判定：{_jd(you)} · 技能：{_skills(you)}"
            f"{' · 翻面' if st.get('flipped_you') else ''}\n"
            f"【AI {me_name}】{max(me['hp'],0)}/{me['maxhp']} 血 · {len(me['hand'])} 手牌 · "
            f"装备：{_eq(me)} · 判定：{_jd(me)} · 技能：{_skills(me)}"
            f"{' · 翻面' if st.get('flipped_me') else ''}\n"
            f"【距离】玩家→AI {distance(you, me)}，AI→玩家 {distance(me, you)} · "
            f"攻击范围 玩家 {attack_range(you)}，AI {attack_range(me)}\n"
            f"{chain_line}{end}{recent}"
        )

    def board_dict(self) -> dict:
        st = self.st
        you, me = st["you"], st["me"]

        def _ch(ch):
            if not ch["hero"]:
                return None
            return {
                "hero": ch["hero"]["n"],
                "hp": max(ch["hp"], 0),
                "maxhp": ch["maxhp"],
                "hand": len(ch["hand"]),
                "equip": [v["n"] for v in ch["equip"].values()],
                "judge": [c["n"] for c in ch["judge"]],
                "skills": [s[0] for s in ch["hero"].get("s", [])],
            }

        has_h = bool(you["hero"] and me["hero"])
        return {
            "you": _ch(you),
            "me": _ch(me),
            "turn": st["turn"],
            "turn_count": st.get("turn_count", 0),
            "first_player": st.get("first_player"),
            "pending": (st["pending"] or {}).get("t"),
            "over": st["over"],
            "distance_you_to_me": distance(you, me) if has_h else None,
            "distance_me_to_you": distance(me, you) if has_h else None,
            "attack_range_you": attack_range(you) if has_h else None,
            "attack_range_me": attack_range(me) if has_h else None,
        }


START_WORDS = ("开一局三国杀", "来一局三国杀", "陪我打三国杀", "三国杀开局", "三国杀单挑", "我要玩三国杀", "想玩三国杀", "玩三国杀", "三国杀", "单挑三国杀")
INPUT_OK = ("0", "过", "结束", "确认", "详情", "技能", "重开", "？", "?", "无懈", "无懈可击", "打无懈", "用无懈", "放行", "不无懈", "算了", "底", "下", "顶", "上", "#", "@", "八卦", "八", "卦", "取消", "♠", "♥", "♣", "♦", "开始", "再来", "下一局", "新局", "重来", "新的一局", "再来一局", "继续", "1", "&", "不出", "不出杀")

def looks_like_input(text):
    t = (text or "").strip()
    if not t or len(t) > 16:
        return False
    if t in INPUT_OK:
        return True
    if t.upper() in ("A", "B", "C", "D", "E") and len(t) == 1:
        return True
    parts = t.replace(",", " ").replace("，", " ").split()
    if not (1 <= len(parts) <= 10):
        return False
    for p in parts:
        if re.match(r"^(顶|底|上|下)?[0-9]{1,2}$", p):
            continue
        if p in ("顶", "底", "上", "下"):
            continue
        if p.upper() in ("A", "B", "C", "D"):
            continue
        return False
    return True