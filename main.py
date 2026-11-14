# 【防吞提示】粘贴后请直接删掉这一行！
# -*- coding: utf-8 -*-
"""AstronBot 插件：三国杀 1v1 文字局（省 token 版 + AI 人格联动 + 武将包 + 双人对抗）"""

import os
import re
import time
import asyncio
import random
import traceback

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter, MessageChain
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Plain, At

from .engine import Game, START_WORDS, looks_like_input
from .heroes import load_hero_packs, SKILL_DESC

_bg_tasks = set()

END_WORDS = (
    "三国杀结束", "结束三国杀", "三国杀退出", "退出三国杀",
    "强制结束", "结束对局",
)
END_REPLY = "行，牌收起来了，这局算你喊停 🔚 想再打就发「/三国杀」"
NO_GAME_REPLY = "现在没开局啊，牌堆都是干净的。想打就发「/三国杀」"

SLASHES = "/／"
TIMING_LOG = "/root/data/plugin_data/sanguosha_timing.log"

SPEAK_FIXED = (
    "you_win", "me_win", "you_dying", "me_dying",
    "start_me_first", "start_you_first"
)

SPEAK_NORMAL = (
    "you_big_hit", "me_big_hit",
    "you_hit", "me_hit",
    "you_sha", "me_sha",
    "you_trick", "me_trick",
    "you_end_turn", "me_end_turn",
    "you_turn_start", "me_turn_start",
    "you_heal", "me_heal",
)

SPEAK_COOLDOWN = 30
SPEAK_CHANCE = 0.10

SURRENDER_WORDS = ("投降", "认输", "我投降", "我认输", "认输投降")


def _write_timing(tag: str, text: str, cost_ms: float):
    try:
        with open(TIMING_LOG, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%m-%d %H:%M:%S')} {tag} {cost_ms:.1f}ms len={len(text)}\n")
    except Exception:
        pass


def strip_slash(text: str) -> str:
    t = (text or "").strip()
    while t and t[0] in SLASHES:
        t = t[1:].strip()
    return t


@register("sanguosha", "鲸鱼", "三国杀 1v1 文字对局（省 token 版 + AI 人格联动 + 武将包 + 双人对抗）", "1.5")
class SanguoshaPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.games: dict[str, Game] = {}
        self._started_at: dict[str, float] = {}
        self.pvp_room: dict = {}
        self._load_packs()

    def _key(self, event: AstrMessageEvent):
        group_id = getattr(event.message_obj, "group_id", None)
        if group_id:
            return f"group_{group_id}"
        return f"friend_{event.get_sender_id()}"

    def _pack_dirs(self):
        here = os.path.dirname(os.path.abspath(__file__))
        builtin = os.path.join(here, "hero_packs")
        user = None
        try:
            from astrbot.api.star import StarTools
            user = os.path.join(str(StarTools.get_data_dir("sanguosha")), "hero_packs")
        except Exception:
            user = None
        return [d for d in (builtin, user) if d]

    def _load_packs(self):
        dirs = self._pack_dirs()
        for d in dirs[1:]:
            try:
                os.makedirs(d, exist_ok=True)
            except Exception:
                pass
        try:
            load_hero_packs(*dirs)
        except Exception as e:
            logger.warning(f"[三国杀] 加载武将包失败: {e}")

    async def _send_pvp_result(self, winner: str, loser_id, loser_name: str, extra_head: str = ""):
        """向群聊发送对局结果，支持 @ 战败者；非群聊降级为纯文本。"""
        if not self.pvp_room:
            return
        group_origin = self.pvp_room.get("group_origin")
        if not group_origin:
            return

        head = extra_head or "◆ 对局结束！"
        is_group = "Group" in str(group_origin)

        if is_group:
            try:
                chain = MessageChain([
                    Plain(f"{head}\n最终胜者：{winner}\n"),
                    At(qq=int(loser_id)),
                    Plain(f" {loser_name} 战败了，房间已解散。"),
                ])
                await self.context.send_message(group_origin, chain)
                return
            except Exception as e:
                logger.warning(f"[三国杀] 群内战败播报（@）失败，降级为纯文本: {e}")

        try:
            await self.context.send_message(
                group_origin,
                MessageChain([Plain(f"{head}\n最终胜者：{winner}\n{loser_name} 战败了，房间已解散。")]),
            )
        except Exception as e:
            logger.warning(f"[三国杀] 战败播报失败: {e}")

    @filter.event_message_type(filter.EventMessageType.ALL, priority=1)
    async def sgs_listener(self, event: AstrMessageEvent):
        t0 = time.perf_counter()
        raw = (event.message_str or "").strip()
        if not raw:
            return
        is_slash = raw[0] in SLASHES
        text = strip_slash(raw)
        if not text:
            return
        key = self._key(event)
        compact = re.sub(r"\s+", "", text)
        sender = str(event.get_sender_id())
        group_id = getattr(event.message_obj, "group_id", None)

        # ================= 双人对局绝对拦截 =================
        if self.pvp_room and self.pvp_room.get("state") == "playing":
            p1 = self.pvp_room["p1"]
            p2 = self.pvp_room["p2"]
            game = self.pvp_room["game"]

            if sender in (p1, p2):
                event.stop_event()

            # 0. 投降处理（最高优先级，群聊/私聊通用，不受出牌拦截影响）
            if sender in (p1, p2) and compact in SURRENDER_WORDS:
                if sender == p1:
                    loser_id, loser_name, winner = p1, "P1", "P2"
                else:
                    loser_id, loser_name, winner = p2, "P2", "P1"
                await self._send_pvp_result(winner, loser_id, loser_name, extra_head=f"◆ {loser_name} 选择了投降！")
                self.pvp_room = {}
                yield self._reply(event, "◆ 已投降。")
                return

            # 1. 查技能指令
            if compact in ("?", "？", "详情", "技能") and sender in (p1, p2):
                p1_hero = game.st["you"]["hero"]
                p2_hero = game.st["me"]["hero"]

                msg = "◆ 双方武将技能\n"
                if p1_hero:
                    msg += f"【P1 {p1_hero['n']}】{p1_hero['hp']}血\n"
                    for name, timing, key in p1_hero["s"]:
                        msg += f"　{name}({timing}):\n　　{SKILL_DESC.get(key, '')}\n"
                if p2_hero:
                    msg += f"\n【P2 {p2_hero['n']}】{p2_hero['hp']}血\n"
                    for name, timing, key in p2_hero["s"]:
                        msg += f"　{name}({timing}):\n　　{SKILL_DESC.get(key, '')}\n"

                yield event.plain_result(msg)
                return

            # 2. 看牌指令
            if compact in ("看牌", "查看手牌", "我的手牌") and sender in (p1, p2):
                if game.st.get("pending") and game.st["pending"].get("t") == "pick":
                    pool = game.st["pick"]["you"] if sender == p1 else game.st["pick"]["me"]
                    msg = "◆ 选将\n"
                    for i, h in enumerate(pool, 1):
                        msg += f"　{i}　{h['n']}　{h['hp']}血\n"
                        for name, timing, key in h["s"]:
                            desc = SKILL_DESC.get(key, "")
                            msg += f"　　　{name}({timing}):{desc}\n"
                    msg += "\n◆ 提示　请直接回复数字 1/2/3 选择你的武将。"
                    yield event.plain_result(msg)
                else:
                    side = "p1" if sender == p1 else "p2"
                    yield event.plain_result(game.private_view(side))
                return

            if sender not in (p1, p2):
                return

            # 3. 选将逻辑
            if game.st.get("pending") and game.st["pending"].get("t") == "pick":
                if not group_id:
                    if text.isdigit() and 1 <= int(text) <= 3:
                        idx = int(text) - 1

                        if sender == p1:
                            if game.st["pick_custom"]["you"]:
                                yield self._reply(event, "◆ 提示　你已经选过武将了。")
                                return
                            game.st["pick_custom"]["you"] = game.st["pick"]["you"][idx]
                            reply_msg = f"◆ 选将成功！\n你选择了：{game.st['pick_custom']['you']['n']}\n请等待对方选将..."
                        else:
                            if game.st["pick_custom"]["me"]:
                                yield self._reply(event, "◆ 提示　你已经选过武将了。")
                                return
                            game.st["pick_custom"]["me"] = game.st["pick"]["me"][idx]
                            reply_msg = f"◆ 选将成功！\n你选择了：{game.st['pick_custom']['me']['n']}\n请等待对方选将..."

                        if game.st["pick_custom"]["you"] and game.st["pick_custom"]["me"]:
                            game._pick_start_custom()
                            p1_name = game.st["you"]["hero"]["n"]
                            p2_name = game.st["me"]["hero"]["n"]
                            first = game.st["first_player"]
                            first_name = p1_name if first == "you" else p2_name

                            group_origin = self.pvp_room.get("group_origin")
                            if group_origin:
                                group_msg = f"◆ 对局开始！\n先手玩家: {first_name}\n（后续对战将在私聊进行，本群仅在结束时公布结果）"
                                try:
                                    await self.context.send_message(group_origin, MessageChain([Plain(group_msg)]))
                                except Exception:
                                    pass

                            await self._send_pvp_views(event, game)
                            yield self._reply(event, f"◆ 选将成功！\n你选择了：{game.st['pick_custom']['you' if sender == p1 else 'me']['n']}\n\n游戏已开始，先手是 {first_name}，请查看私聊面板！")
                            return
                        else:
                            yield self._reply(event, reply_msg)
                            return
                    else:
                        yield self._reply(event, "◆ 提示　请直接回复数字 1/2/3 选择你的武将。")
                        return
                else:
                    yield self._reply(event, "◆ 提示　请前往私聊发送数字 1/2/3 选将。")
                    return

            # 4. 出牌逻辑拦截
            current_actor = self._pvp_actor(game)
            actor_id = p1 if current_actor == "p1" else p2

            if group_id:
                if looks_like_input(text) and not text.startswith('/'):
                    yield self._reply(event, "◆ 提示　为了保护隐私，请前往私聊进行出牌操作。")
                    return
                return

            if not group_id:
                if sender != actor_id:
                    yield self._reply(event, "◆ 提示　还没轮到你操作！")
                    return

                if not looks_like_input(text):
                    yield self._reply(event, "◆ 提示　指令错误。请输入数字出牌、字母用技能、0结束出牌。")
                    return

                swapped = False
                if current_actor == "p2":
                    swapped = True
                    game.swap_all_sides()

                try:
                    game.msg.clear()
                    result = game.handle(text)
                except Exception as e:
                    logger.error(f"[三国杀][PVP] 游戏处理出错: {e}\n{traceback.format_exc()}")
                    yield self._reply(event, "◆ 提示　游戏遇到异常，请重试或发「/投降」")
                    return
                finally:
                    if swapped:
                        game.swap_all_sides()

                if game.st.get("over"):
                    winner = "P1" if game.st["over"] == "you" else "P2"
                    loser_id = p2 if winner == "P1" else p1
                    loser_name = "P2" if winner == "P1" else "P1"
                    await self._send_pvp_result(winner, loser_id, loser_name)
                    self.pvp_room = {}
                else:
                    await self._send_pvp_views(event, game, result, current_actor)
                return
        # ====================================================

        # ================= 等待加入阶段的解散 =================
        if self.pvp_room and self.pvp_room.get("state") == "waiting_join":
            if sender == self.pvp_room.get("p1") and compact in ("取消", "解散", "解散房间", "投降", "认输"):
                event.stop_event()
                self.pvp_room = {}
                yield self._reply(event, "◆ 房间已解散。")
                return
        # ====================================================

        # ================= 统一指令分发入口 =================
        if "三国杀重载武将" in compact:
            event.stop_event()
            try:
                from .heroes import HEROES
                n = load_hero_packs(*self._pack_dirs())
                yield self._reply(event, f"武将包已重载，本次处理 {n} 个。当前武将总数：{len(HEROES)}")
            except Exception as e:
                yield self._reply(event, f"重载失败：{e}")
            return

        if "三国杀" in compact and ("help" in compact.lower() or "帮助" in compact):
            event.stop_event()
            help_msg = (
                "◆ 三国杀插件指令大全\n"
                "【模式与房间】\n"
                "  /三国杀 - 开启单人vsAI对局\n"
                "  /三国杀双人 - 创建双人房间(群内)\n"
                "  /三国杀加入 - 加入双人房间(群内)\n"
                "  /投降 或 投降 - 双人对局中认输\n"
                "【局内操作】\n"
                "  双人模式下，选将、出牌、看牌均在【私聊】进行\n"
                "  数字(如 1) - 打出对应序号的手牌\n"
                "  字母(如 A) - 发动对应的技能\n"
                "  0 - 过/放弃/取消/结束出牌\n"
                "  ? - 查看双方武将技能\n"
                "【其他】\n"
                "  /结束 或 /三国杀结束 - 强制终止当前对局\n"
            )
            yield self._reply(event, help_msg)
            return

        if "三国杀双人" in compact:
            event.stop_event()
            if self.pvp_room:
                yield self._reply(event, "当前已经有双人房间了，请发「/三国杀加入」。")
                return
            self.pvp_room = {
                "p1": sender,
                "p2": None,
                "game": None,
                "state": "waiting_join",
                "group_origin": event.unified_msg_origin
            }
            yield self._reply(event, "◆ 双人对战房间已创建！\n请另一位玩家在群里发送「/三国杀加入」参与对局。")
            return

        if "三国杀加入" in compact:
            event.stop_event()
            if not self.pvp_room or self.pvp_room.get("state") != "waiting_join":
                yield self._reply(event, "当前没有正在等待加入的双人房间。")
                return
            if sender == self.pvp_room["p1"]:
                yield self._reply(event, "你自己不能和自己打双人啊！")
                return

            self.pvp_room["p2"] = sender
            self.pvp_room["state"] = "playing"

            game = Game()
            game.is_pvp = True
            self.pvp_room["game"] = game
            game.start()

            yield self._reply(event, "◆ 双方玩家已就位！\n【选将阶段】请双方立刻私聊机器人发送「看牌」，然后私聊发送数字 1/2/3 选择你的武将。")
            return

        # ================= 单人游戏逻辑 =================
        if self.pvp_room:
            return

        game = self.games.get(key)
        hit_end = any(w in compact for w in END_WORDS) or (
            is_slash and compact in ("结束", "退出", "不玩了")
        )

        if game is None:
            if hit_end:
                event.stop_event()
                yield self._done(event, NO_GAME_REPLY, t0, "no_game")
                return

            if len(compact) <= 16 and any(w in compact for w in START_WORDS) \
                    and not any(w in compact for w in ("怎么", "规则", "教程", "插件", "介绍", "双人", "加入", "help", "帮助")):
                game = Game()
                self.games[key] = game
                self._started_at[key] = time.time()
                event.stop_event()

                task = asyncio.create_task(self._bg_speak(event, game))
                _bg_tasks.add(task)
                task.add_done_callback(_bg_tasks.discard)

                yield self._done(event, game.start(), t0, "start")
            return

        if hit_end:
            self.games.pop(key, None)
            event.stop_event()
            yield self._reply(event, END_REPLY)
            return

        if text == "重开":
            game.st["pending"] = {"t": "restart"}
            event.stop_event()
            yield self._done(event, "要放弃当前战局重开？回「确认」就重开，回别的继续打", t0, "restart")
            return

        p_cur = game.st.get("pending") if game else None

        is_zhiyi = False
        if p_cur and p_cur.get("t") == "zhiyi_opt":
            if re.match(r"^\d+\s*[stjfl]?$", text.lower()) or text in ("0", "过"):
                is_zhiyi = True

        if not looks_like_input(text) and not (p_cur and p_cur.get("t") in ("pick_self_name", "pick_opp_name")) and not is_zhiyi:
            return

        try:
            game.msg.clear()
            result = game.handle(text)
            if result == "RESTART":
                self.games[key] = Game()
                result = self.games[key].start()
        except Exception as e:
            logger.error(f"[三国杀] 游戏处理出错: {e}\n{traceback.format_exc()}")
            result = "◆ 提示　游戏遇到异常，请重试或发「/结束」"

        event.stop_event()

        task = asyncio.create_task(self._bg_speak(event, game))
        _bg_tasks.add(task)
        task.add_done_callback(_bg_tasks.discard)

        yield self._done(event, result, t0, "play")

    def _replace_waiting(self, view, msg):
        lines = view.split('\n')
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith("◆ 选项"):
                lines[i] = "◆ 选项　" + msg
            elif lines[i].startswith("◆ 阶段"):
                lines[i] = "◆ 阶段　" + msg
        return '\n'.join(lines)

    def _pvp_actor(self, game):
        owner = None
        if hasattr(game, "pending_owner"):
            owner = game.pending_owner()
        if owner is None:
            owner = game.st.get("turn")
        return "p1" if owner == "you" else "p2"

    async def _send_pvp_views(self, event: AstrMessageEvent, game: Game, result: str = "", actor: str = ""):
        if not self.pvp_room:
            return

        p1 = self.pvp_room["p1"]
        p2 = self.pvp_room["p2"]

        p1_name = game.st["you"]["hero"]["n"] if game.st["you"]["hero"] else "P1"
        p2_name = game.st["me"]["hero"]["n"] if game.st["me"]["hero"] else "P2"

        broadcast_text = "\n".join(game.msg)
        game.msg.clear()

        next_actor = self._pvp_actor(game)
        next_name = p1_name if next_actor == "p1" else p2_name

        if result and actor:
            operator_view = result
            opponent_side = "p2" if actor == "p1" else "p1"
            opponent_view = game.private_view(opponent_side)

            if broadcast_text:
                broadcast_text = f"──────────────\n◆ 播报\n" + "\n".join(f"　{m}" for m in broadcast_text.split('\n')) + "\n──────────────\n\n"
                opponent_view = broadcast_text + opponent_view

            p1_view = operator_view if actor == "p1" else opponent_view
            p2_view = operator_view if actor == "p2" else opponent_view

            if next_actor != actor:
                if actor == "p1":
                    p1_view = self._replace_waiting(p1_view, f"等待 {next_name} 行动")
                else:
                    p2_view = self._replace_waiting(p2_view, f"等待 {next_name} 行动")
            if next_actor != opponent_side:
                if opponent_side == "p1":
                    p1_view = self._replace_waiting(p1_view, f"等待 {next_name} 行动")
                else:
                    p2_view = self._replace_waiting(p2_view, f"等待 {next_name} 行动")
        else:
            p1_view = game.private_view("p1")
            p2_view = game.private_view("p2")
            if broadcast_text:
                broadcast_text = f"──────────────\n◆ 播报\n" + "\n".join(f"　{m}" for m in broadcast_text.split('\n')) + "\n──────────────\n\n"
                p1_view = broadcast_text + p1_view
                p2_view = broadcast_text + p2_view

            if next_actor == "p1":
                p2_view = self._replace_waiting(p2_view, f"等待 {p1_name} 行动")
            else:
                p1_view = self._replace_waiting(p1_view, f"等待 {p2_name} 行动")

        bot = getattr(event, "bot", None)
        if bot and hasattr(bot, "api"):
            try:
                await bot.api.call_action("send_private_msg", user_id=int(p1), message=p1_view)
                await bot.api.call_action("send_private_msg", user_id=int(p2), message=p2_view)
            except Exception as e:
                logger.warning(f"[三国杀] 底层私聊失败: {e}")
        else:
            try:
                p1_origin = f"aiocqhttp:FriendMessage:{p1}"
                p2_origin = f"aiocqhttp:FriendMessage:{p2}"
                await self.context.send_message(p1_origin, MessageChain([Plain(p1_view)]))
                await self.context.send_message(p2_origin, MessageChain([Plain(p2_view)]))
            except Exception as e:
                logger.warning(f"[三国杀] 默认私聊失败: {e}")

    async def _bg_speak(self, event: AstrMessageEvent, game: Game):
        try:
            extra = await self._maybe_speak_llm(event, game)
            if extra:
                try:
                    await event.send(event.plain_result(extra))
                except Exception:
                    chain = MessageChain([Plain(extra)])
                    await self.context.send_message(event.unified_msg_origin, chain)
        except Exception as e:
            logger.error(f"[三国杀] 后台插话异常: {e}\n{traceback.format_exc()}")

    @filter.on_llm_request()
    async def inject_board_into_llm(self, event: AstrMessageEvent, req: ProviderRequest):
        key = self._key(event)
        game = self.games.get(key)
        if not game:
            return
        try:
            summary = game.public_summary()
        except Exception as e:
            return
        if not summary:
            return

        inject = (
            "\n\n【系统提示：当前你和玩家正在进行一局 1v1 三国杀单挑】\n"
            "下面是实时牌局状态，请仔细阅读。玩家随时可能在游戏内外问你战况、要建议、吐槽。\n"
            f"{summary}\n\n"
            "聊天规则：用你当前的人设自然回应，不要输出游戏 UI、数字序号。结合局势共情：血少可以嘴硬，血多可以得意。\n"
        )

        if req.prompt:
            req.prompt = f"{req.prompt}\n\n[隐藏牌局数据]：{inject}"
        else:
            req.prompt = inject

    async def _get_persona_prompt(self, event: AstrMessageEvent) -> str:
        try:
            conv_mgr = getattr(self.context, "conversation_manager", None)
            if conv_mgr is None:
                return ""
            conv_id = await conv_mgr.get_curr_conversation_id(event.unified_msg_origin)
            if not conv_id:
                return ""
            conv = await conv_mgr.get_conversation(event.unified_msg_origin, conv_id)
            if not conv:
                return ""

            persona_id = getattr(conv, "persona_id", None)
            persona_mgr = getattr(self.context, "persona_manager", None)
            if persona_mgr is None:
                return ""

            persona = None
            if persona_id:
                getter = getattr(persona_mgr, "get_persona", None) or getattr(persona_mgr, "get_persona_by_id", None)
                if getter:
                    persona = await getter(persona_id)

            if not persona:
                getter_default = getattr(persona_mgr, "get_default_persona_v3", None)
                if getter_default:
                    persona = await getter_default()

            if persona and getattr(persona, "system_prompt", None):
                return persona.system_prompt
        except Exception as e:
            logger.warning(f"[三国杀] 获取人格失败: {e}")
        return ""

    async def _maybe_speak_llm(self, event: AstrMessageEvent, game: Game):
        if game.st.get("_is_speaking"):
            return None
        game.st["_is_speaking"] = True

        try:
            events = game.take_llm_events()
            if not events:
                return None

            fixed = next((e for e in events if e.get("kind") in SPEAK_FIXED), None)
            hit = fixed

            if not hit:
                normal = next((e for e in events if e.get("kind") in SPEAK_NORMAL), None)
                if normal:
                    now = time.time()
                    last = getattr(game, "_last_speak_ts", 0.0)
                    if now - last >= SPEAK_COOLDOWN:
                        if random.random() < SPEAK_CHANCE:
                            hit = normal
                            game._last_speak_ts = now

            if not hit:
                return None

            try:
                provider = self.context.get_using_provider()
                if provider is None:
                    return None

                prompt = game.build_llm_prompt(hit)
                persona_prompt = await self._get_persona_prompt(event)

                self_talk_sid = f"{event.unified_msg_origin}__sgs_speak"

                try:
                    if persona_prompt:
                        resp = await provider.text_chat(
                            prompt=prompt,
                            session_id=self_talk_sid,
                            system_prompt=persona_prompt,
                        )
                    else:
                        resp = await provider.text_chat(
                            prompt=prompt,
                            session_id=self_talk_sid,
                        )
                except TypeError:
                    resp = await provider.text_chat(
                        prompt=prompt,
                        session_id=self_talk_sid,
                    )

                line = (getattr(resp, "completion_text", "") or "").strip()
                line = line.strip('"“”「」『』 ')
                line = re.sub(r"\s+", " ", line).strip()
                if not line:
                    return None
                if len(line) > 60:
                    line = line[:60]

                return line
            except Exception as e:
                logger.warning(f"[三国杀] LLM 请求失败: {e}")
                return None
        finally:
            game.st["_is_speaking"] = False

    def _done(self, event: AstrMessageEvent, text: str, t0: float, tag: str):
        _write_timing(tag, text, (time.perf_counter() - t0) * 1000)
        return self._reply(event, text)

    @staticmethod
    def _reply(event: AstrMessageEvent, text: str):
        return event.plain_result(text)
