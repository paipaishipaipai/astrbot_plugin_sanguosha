# -*- coding: utf-8 -*-
"""技能 API：技能代码通过它访问游戏状态，不直接碰 engine 内部。"""


class SkillAPI:
    def __init__(self, game, who):
        self.game = game
        self.who = who

    @property
    def state(self):
        return self.game.st

    @property
    def me(self):
        return self.game.st[self.who]

    @property
    def opp(self):
        return self.game.st[self.game._opp(self.who)]

    @property
    def hand(self):
        return self.me["hand"]

    @property
    def hp(self):
        return self.me["hp"]

    @property
    def maxhp(self):
        return self.me["maxhp"]

    @property
    def equip(self):
        return self.me["equip"]

    @property
    def judge_area(self):
        return self.me["judge"]

    @property
    def deck(self):
        return self.game.deck

    @property
    def is_my_turn(self):
        return self.game.st["turn"] == self.who

    @property
    def is_over(self):
        return bool(self.game.st.get("over"))

    def draw(self, n=1):
        return self.game.draw(self.who, n)

    def discard(self, card, is_play=False):
        self.game._discard(self.who, card, is_play=is_play)

    def hand_out(self, card):
        self.game._hand_out(self.who, card)

    def hurt(self, target, dmg, card=None, element=None):
        self.game.hurt(target, dmg, self.who, card=card, element=element)

    def heal(self, n=1):
        self.me["hp"] = min(self.me["hp"] + n, self.me["maxhp"])
        self.game._check_jieyin()

    def judge(self, why):
        return self.game.judge(self.who, why)

    def say(self, text):
        self.game.say(text)

    def steal_from(self, target, card):
        self.game._steal(target, card, self.who)

    def pick_card_from(self, target, allow_judge=True):
        return self.game._pick_card(target, allow_judge=allow_judge)

    def equip_card(self, card):
        self.game._equip_card(self.who, card)

    def has_equip(self, slot):
        return slot in self.me["equip"]

    def weapon(self):
        return self.game.wep(self.me)

    def armor(self):
        return self.game.armor(self.me)

    def distance_to(self, target="opp"):
        t = self.opp if target == "opp" else self.me
        return self.game.distance(self.me, t)

    def attack_range(self):
        return self.game.attack_range(self.me)

    def in_range(self):
        return self.game.in_attack_range(self.me, self.opp)

    def all_cards_of(self, target="me"):
        ch = self.me if target == "me" else self.opp
        return list(ch["hand"]) + [v for v in ch["equip"].values()] + list(ch["judge"])

    def is_flipped(self):
        return bool(self.game.st.get(f"flipped_{self.who}"))

    def set_flipped(self, flag=True):
        self.game.st[f"flipped_{self.who}"] = bool(flag)

    def card_in_hand(self, name):
        for c in self.hand:
            if c["n"] == name:
                return c
        return None

    def has_card_in_hand(self, name):
        return self.card_in_hand(name) is not None