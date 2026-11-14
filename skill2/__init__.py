# -*- coding: utf-8 -*-
"""技能包 skill2：所有技能统一放在 builtin.py，engine.py 通过 dispatch 分发。

支持的钩子：
    on_prepare_phase(api)                        准备阶段
    on_modify_draw_count(api) -> int             摸牌阶段，返回额外摸牌数
    on_end_phase(api)                            结束阶段
    on_damaged(api, dmg, src, card, element)     受到伤害后
    on_damage_dealt(api, target, dmg, card, element)  造成伤害后
    on_judge_replace(api, card, why) -> card     判定牌生效前（返回新牌则替换）
    on_judge_after(api, card, why)               判定牌生效后
    on_equip_lost(api, card)                     失去装备时
    on_sha_target(api, sha_card, target_who) -> dict | None
        使用杀指定目标后，返回 {"no_shan": True, "dmg_bonus": 1} 之类
"""

import traceback
from astrbot.api import logger

SKILL_REGISTRY = {}
_LOADED = False


def skill(name):
    def wrapper(cls):
        SKILL_REGISTRY.setdefault(name, []).append(cls())
        return cls
    return wrapper


def get_skills(who_state):
    if not who_state.get("hero"):
        return []
    out = []
    for s in who_state["hero"].get("s", []):
        cn = s[0]
        for inst in SKILL_REGISTRY.get(cn, []):
            out.append(inst)
    return out


def dispatch(game, who, hook, *args, **kwargs):
    results = []
    for inst in get_skills(game.st[who]):
        fn = getattr(inst, hook, None)
        if fn is None:
            continue
        try:
            results.append(fn(*args, **kwargs))
        except Exception as e:
            logger.error(f"[三国杀][skill2] {type(inst).__name__}.{hook} 出错: {e}")
            logger.error(traceback.format_exc())
    return results


def dispatch_first(game, who, hook, *args, default=None, **kwargs):
    for inst in get_skills(game.st[who]):
        fn = getattr(inst, hook, None)
        if fn is None:
            continue
        try:
            r = fn(*args, **kwargs)
            if r is not None:
                return r
        except Exception as e:
            logger.error(f"[三国杀][skill2] {type(inst).__name__}.{hook} 出错: {e}")
            logger.error(traceback.format_exc())
    return default


def import_all_skills():
    global _LOADED
    if _LOADED:
        return
    try:
        from . import builtin  # noqa: F401
    except Exception as e:
        logger.error(f"[三国杀][skill2] 加载 builtin 失败: {e}")
        logger.error(traceback.format_exc())
        return
    _LOADED = True
    logger.info(f"[三国杀][skill2] 已加载 {len(SKILL_REGISTRY)} 种技能")
