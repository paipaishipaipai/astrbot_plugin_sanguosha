# -*- coding: utf-8 -*-
"""三国杀武将数据 + 武将包加载器"""

import os
import json

D = "锁定技"

HEROES = [
    {"n": "曹操", "hp": 4, "g": "M", "s": [("奸雄", "受到伤害后", "jianxiong")]},
    {"n": "司马懿", "hp": 3, "g": "M", "s": [("反馈", "受到伤害后", "fankui"), ("鬼才", "判定时", "guicai")]},
    {"n": "夏侯惇", "hp": 4, "g": "M", "s": [("刚烈", "受到伤害后", "ganglie"), ("清俭", "每轮限一次", "qingjian")]},
    {"n": "张辽", "hp": 4, "g": "M", "s": [("突袭", "摸牌阶段", "tuxi")]},
    {"n": "许褚", "hp": 5, "g": "M", "s": [("裸衣", "造成杀/决斗伤害后", "luoyi")]},
    {"n": "郭嘉", "hp": 3, "g": "M", "s": [("天妒", "判定时", "tiandu"), ("遗计", "受到伤害后", "yiji")]},
    {"n": "甄姬", "hp": 3, "g": "F", "s": [("洛神", "准备阶段", "luoshen"), ("倾国", "需要闪时", "qingguo")]},
    {"n": "魏延", "hp": 4, "g": "M", "s": [("狂骨", "造成伤害后", "kuanggu"), ("奇谋", "限定技", "qimou")]},
    {"n": "界关羽", "hp": 4, "g": "M", "s": [("武圣", "出牌阶段", "wusheng"), ("义绝", "出牌阶段限一次", "yijue")]},
    {"n": "界张飞", "hp": 4, "g": "M", "s": [("咆哮", D, "paoxiao"), ("厉勇", "杀被闪抵消后", "liyong")]},
    {"n": "诸葛亮", "hp": 3, "g": "M", "s": [("观星", "准备阶段", "guanxing"), ("空城", D, "kongcheng")]},
    {"n": "界赵云", "hp": 4, "g": "M", "s": [("龙胆", "出牌阶段/需要杀闪时", "longdan"), ("涯角", "回合外打出基本牌", "yajiao")]},
    {"n": "马超", "hp": 4, "g": "M", "s": [("马术", D, "mashu"), ("铁骑", "使用杀时", "tieqi")]},
    {"n": "黄月英", "hp": 3, "g": "F", "s": [("集智", "使用锦囊时", "jizhi"), ("奇才", D, "qicai")]},
    {"n": "孙权", "hp": 4, "g": "M", "s": [("制衡", "出牌阶段", "zhiheng")]},
    {"n": "甘宁", "hp": 4, "g": "M", "s": [("奇袭", "出牌阶段", "qixi")]},
    {"n": "凌统", "hp": 4, "g": "M", "s": [("旋风", "失去装备时", "xuanfeng")]},
    {"n": "黄盖", "hp": 4, "g": "M", "s": [("苦肉", "出牌阶段", "kurou")]},
    {"n": "周瑜", "hp": 3, "g": "M", "s": [("英姿", "摸牌阶段", "yingzi"), ("反间", "出牌阶段", "fanjian")]},
    {"n": "孙坚", "hp": 4, "g": "M", "s": [("英魂", "准备阶段", "yinghun")]},
    {"n": "陆逊", "hp": 3, "g": "M", "s": [("谦逊", D, "qianxun"), ("连营", "失去最后手牌时", "lianying")]},
    {"n": "孙尚香", "hp": 3, "g": "F", "s": [("结姻", "每轮限一次", "jieyin"), ("枭姬", "失去装备时", "xiaoji")]},
    {"n": "华佗", "hp": 3, "g": "M", "s": [("急救", "濒死时", "jijiu"), ("青囊", "出牌阶段", "qingnang"), ("除疠", "进入濒死状态时", "chuli")]},
    {"n": "界吕布", "hp": 4, "g": "M", "s": [("无双", D, "wushuang"), ("利驭", "杀造成伤害后", "liyu")]},
    {"n": "界庞德", "hp": 4, "g": "M", "s": [("马术", D, "mashu"), ("鞬出", "使用杀时", "jiangu")]},
    {"n": "曹仁", "hp": 4, "g": "M", "s": [("据守", "结束阶段", "jushou"), ("解围", "需要无懈可击时", "jiewei")]},
    {"n": "黄忠", "hp": 4, "g": "M", "s": [("烈弓", "使用杀指定目标后", "liegong")]},
    {"n": "孙策", "hp": 4, "g": "M", "s": [("激昂", "使用/被红色杀/决斗时", "jiangtang"), ("魂姿", "准备阶段", "hunzi")]},
    {"n": "凌操", "hp": 4, "g": "M", "s": [("独进", "摸牌阶段", "dujin")]},
    {"n": "曹植", "hp": 3, "g": "M", "s": [("落英", "回合外弃牌时", "luoying"), ("酒诗", "出牌阶段/受伤时", "jiushi"), ("成章", "受到伤害后", "chengzhang")]},
]

SKILL_DESC = {
    "jianxiong": "受到伤害后,获得造成伤害的牌,然后摸1张",
    "fankui": "受到伤害后,获得来源一张牌(0=随机手牌,1=武器,2=防具,3=-1马,4=+1马)",
    "guicai": "判定牌生效前,可打出一张手牌替换判定牌",
    "ganglie": "受到伤害后判定,若不为红桃,来源弃2张手牌或受1点伤害",
    "qingjian": "每轮限一次,有牌不因使用/打出进入弃牌堆时,可获得之",
    "tuxi": "摸牌阶段,改为获得对手一张手牌,然后摸1张",
    "luoyi": "造成杀/决斗伤害后,可弃一张手牌,对该角色造成1点额外伤害",
    "tiandu": "判定牌生效后,获得之",
    "yiji": "受到伤害后摸2张(每点伤害触发一次)",
    "luoshen": "准备阶段判定,黑色则获得并继续,红色则停止",
    "qingguo": "黑色手牌可当闪使用或打出",
    "kuanggu": "造成伤害后,选择回复1点体力或摸1张",
    "qimou": "限定技,出牌阶段失去任意点体力,本回合杀次数+X,距离-X",
    "wusheng": "可将一张红色牌当杀使用或打出",
    "yijue": "出牌阶段限一次,弃一张牌令对手展示一张手牌.黑色则本回合对其杀伤害+1,红色则获得之",
    "paoxiao": "锁定技,使用杀无次数限制",
    "liyong": "杀被闪抵消后,下一张杀无视距离,伤害+1,目标不可响应",
    "guanxing": "准备阶段,观看牌堆顶3张并调整顺序",
    "kongcheng": "锁定技,无手牌时不能成为杀/决斗目标",
    "longdan": "可将杀当闪,闪当杀使用或打出",
    "yajiao": "回合外打出基本牌时,展示牌堆顶一张,若为基本牌则获得之(每回合限一次)",
    "mashu": "锁定技,计算距离-1",
    "tieqi": "使用杀指定目标后判定,目标需弃一张同花色牌才能响应",
    "jizhi": "使用非延时锦囊时,摸1张",
    "qicai": "锁定技,使用锦囊无距离限制",
    "zhiheng": "出牌阶段限一次,弃任意张牌,然后摸等量的牌",
    "qixi": "黑色牌可当过河拆桥使用",
    "xuanfeng": "失去装备区里的牌时,可依次弃对手两张牌;弃牌阶段弃置至少两张牌时,也可依次弃对手两张牌",
    "kurou": "出牌阶段,失去1点体力,然后摸2张",
    "yingzi": "摸牌阶段,多摸1张",
    "fanjian": "出牌阶段限一次,扣一张手牌给对手猜花色.猜错则对手受1点伤害,无论对错对手获得该牌",
    "yinghun": "准备阶段,若已受伤,可令对手摸1张,然后弃X张(X为已损失体力)",
    "qianxun": "锁定技,不能成为顺手牵羊/乐不思蜀的目标",
    "lianying": "失去最后一张手牌时,摸1张",
    "jieyin": "每轮限一次,有角色回复体力时,可摸1张",
    "xiaoji": "失去装备区里的牌时,摸2张",
    "jijiu": "回合外,可将红色牌当桃使用",
    "qingnang": "出牌阶段限一次,弃一张手牌,令一名角色回复1点体力",
    "wushuang": "锁定技,使用的杀需2张闪才能抵消;决斗中对手每次需打出2张杀",
    "liyu": "使用杀造成伤害后,获得受伤角色一张牌,然后其摸1张",
    "jiangu": "使用杀指定目标后,可弃其一张牌.若不为基本牌,该角色不能出闪,然后你摸1张",
    "zhangba_skill": "出牌阶段按&,回两张手牌序号(空格分隔),视为使用一张普通杀",
    "jushou": "结束阶段,可翻面并摸4张牌,然后弃一张手牌;若为装备牌,则使用之",
    "jiewei": "可将一张装备牌当无懈可击使用或打出",
    "liegong": "使用杀指定目标后,若其手牌数大于你则不能出闪;若其体力值大于你则此杀伤害+1",
    "chuli": "进入濒死状态时,摸1张",
    "jiangtang": "使用红色杀/被红色杀指定/使用决斗/被决斗指定时,各摸1张",
    "hunzi": "准备阶段,若体力值为1,失去1点体力上限,获得\"英姿\"和\"英魂\"",
    "dujin": "摸牌阶段,额外摸1+X张牌(X为装备区牌数的一半,向下取整)",
    "luoying": "回合外,有梅花牌不因使用/打出进入弃牌堆时,获得之",
    "jiushi": "正面朝上时,可翻面视为使用一张酒;背面朝上受到伤害时,可翻面;从背面翻至正面时,摸1张",
    "chengzhang": "受到伤害后获得一个章标记;有7个章标记时,清除所有并回复1点体力,摸2张",
}


ENGINE_SKILL_KEYS = set(SKILL_DESC.keys()) - {"zhangba_skill"}


def _load_one_pack(path: str) -> int:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[三国杀][武将包] 读取失败 {path}: {e}")
        return 0

    added = 0
    pack_name = data.get("pack_name") or os.path.basename(path)

    for k, v in (data.get("skill_desc") or {}).items():
        if k not in SKILL_DESC:
            SKILL_DESC[k] = v

    for h in data.get("heroes") or []:
        if not isinstance(h, dict):
            continue
        name = h.get("n")
        hp = h.get("hp")
        skills = h.get("s")
        if not name or not isinstance(hp, int) or not isinstance(skills, list):
            print(f"[三国杀][武将包] {pack_name} 字段不全，跳过: {h}")
            continue

        norm_skills = []
        bad = False
        for s in skills:
            if not isinstance(s, (list, tuple)) or len(s) != 3:
                print(f"[三国杀][武将包] {name} 技能格式错误: {s}")
                bad = True
                break
            norm_skills.append((str(s[0]), str(s[1]), str(s[2])))
        if bad:
            continue

        for cn, _timing, key in norm_skills:
            if key not in ENGINE_SKILL_KEYS:
                print(f"[三国杀][武将包] 警告：{name} 的技能「{cn}」({key}) 未登记描述")

        hero = {"n": str(name), "hp": int(hp), "g": str(h.get("g", "M")), "s": norm_skills}

        existing_idx = next((i for i, x in enumerate(HEROES) if x["n"] == hero["n"]), -1)
        if existing_idx >= 0:
            HEROES[existing_idx] = hero
            print(f"[三国杀][武将包] 覆盖武将: {hero['n']}（来自 {pack_name}）")
        else:
            HEROES.append(hero)
            print(f"[三国杀][武将包] 新增武将: {hero['n']}（来自 {pack_name}）")
        added += 1
    return added


def load_hero_packs(*dirs: str) -> int:
    total = 0
    for d in dirs:
        if not d or not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.lower().endswith(".json"):
                continue
            total += _load_one_pack(os.path.join(d, fn))
    if total:
        print(f"[三国杀][武将包] 加载完成，共 {total} 个武将，当前总武将数 {len(HEROES)}")
    return total