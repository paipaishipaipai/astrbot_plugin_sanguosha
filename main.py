# -*- coding: utf-8 -*-
"""AstronBot 插件：三国杀 1v1 文字局

开局：「/三国杀」（也可以用「三国杀」「开一局三国杀」「陪我打三国杀」）
选将：1/2/3 从候选选自己；A=指定自己武将 B=指定敌人武将 0=用已指定开始
对局中：回数字出牌 / 字母用技能 / 0 结束出牌
强制收摊：「/结束」「/退出三国杀」「三国杀结束」
游戏外：直接和 AI 聊天，AI 会自动"看到"当前牌局并陪你聊

会话隔离：
- 游戏内出牌结果：不走 LLM，直接拼字符串，不进聊天历史
- AI 主动台词：走独立 session（{origin}__sgs_speak），不污染聊天历史
- 玩家游戏外聊天：走默认 session，AI 通过 on_llm_request 看到牌局摘要
"""

import os
import re
import time

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Context, Star, register
# 新增：用于临时注入上下文的 TextPart 和 获取数据目录的 StarTools
from astrbot.api.message import TextPart  
from astrbot.api.star import StarTools

from .engine import Game, START_WORDS, looks_like_input
from .heroes import load_hero_packs

# 强制结束对局：命中就立刻清桌，不管当前什么阶段
END_WORDS = (
    "三国杀结束", "结束三国杀", "三国杀退出", "退出三国杀",
    "强制结束", "结束对局",
)
END_REPLY = "行，牌收起来了，这局算你喊停 🔚 想再打就发「/三国杀」"
NO_GAME_REPLY = "现在没开局啊，牌堆都是干净的。想打就发「/三国杀」"

SLASHES = "/／"

# 高优先级事件：胜负/濒死，无视冷却，立刻说
SPEAK_URGENT = ("you_win", "me_win", "you_dying", "me_dying")

# 普通事件：日常操作，有冷却，说一句看局势的反应
SPEAK_NORMAL = (
    "start_me_first", "start_you_first",
    "you_big_hit", "me_big_hit",
    "you_hit", "me_hit",
    "you_sha", "me_sha",
    "you_trick", "me_trick",
    "you_end_turn", "me_end_turn",
    "you_turn_start", "me_turn_start",
    "you_heal", "me_heal",
)

# 普通事件两次主动说话的冷却秒数
SPEAK_COOLDOWN = 15

# 是否让 AI 主动说话时带上当前会话人格
AI_SPEAK_USE_PERSONA = True

# AI 主动台词的独立 session 后缀（和玩家聊天历史隔离）
SELF_TALK_SUFFIX = "__sgs_speak"


def _write_timing(tag: str, text: str, cost_ms: float):
    try:
        # 修改：使用 StarTools 动态获取数据目录，避免硬编码 /root 导致权限报错
        data_dir = StarTools.get_data_dir("sanguosha")
        log_path = os.path.join(str(data_dir), "sanguosha_timing.log")
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(
                f"{time.strftime('%m-%d %H:%M:%S')} {tag} "
                f"{cost_ms:.1f}ms len={len(text)}\n"
            )
    except Exception:
        pass


def strip_slash(text: str) -> str:
    t = (text or "").strip()
    while t and t[0] in SLASHES:
        t = t[1:].strip()
    return t


# 修改：版本号从 1.9.0 改为 1.4.0，与 metadata.yaml 保持一致
@register("sanguosha", "鲸鱼", "三国杀 1v1 文字对局（省 token 版 + AI 人格联动 + 武将包）", "1.4.0")
class SanguoshaPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.games: dict[str, Game] = {}
        self._started_at: dict[str, float] = {}
        self._load_packs()

    def _key(self, event: AstrMessageEvent):
        return f"{event.unified_msg_origin}"

    # ─────────────────────────────────────────────
    # 武将包：目录与加载
    # ─────────────────────────────────────────────
    def _pack_dirs(self):
        here = os.path.dirname(os.path.abspath(__file__))
        builtin = os.path.join(here, "hero_packs")
        user = None
        try:
            user = os.path.join(str(StarTools.get_data_dir("sanguosha")), "hero_packs")
        except Exception:
            user = None
        return [d for d in (builtin, user) if d]

    def _load_packs(self):
        dirs = self._pack_dirs()
        # 自动给用户目录建好，方便直接丢文件
        for d in dirs[1:]:
            try:
                os.makedirs(d, exist_ok=True)
            except Exception:
                pass
        try:
            load_hero_packs(*dirs)
        except Exception as e:
            logger.warning(f"[三国杀] 加载武将包失败: {e}")

    @filter.command("三国杀重载武将")
    async def sgs_reload_heroes(self, event: AstrMessageEvent):
        event.stop_event()
        try:
            from .heroes import HEROES
            n = load_hero_packs(*self._pack_dirs())
            yield self._reply(event, f"武将包已重载，本次处理 {n} 个。当前武将总数：{len(HEROES)}")
        except Exception as e:
            yield self._reply(event, f"重载失败：{e}")

    # ─────────────────────────────────────────────
    # 斜杠开局
    # ─────────────────────────────────────────────
    @filter.command("三国杀")
    async def sgs_slash_start(self, event: AstrMessageEvent):
        key = self._key(event)
        if self.games.get(key) is not None:
            if time.time() - self._started_at.get(key, 0) < 3:
                return
            event.stop_event()
            yield self._reply(event, "牌已经在桌上了，直接回数字出牌；想收摊就发「/结束」")
            return
        game = Game()
        self.games[key] = game
        self._started_at[key] = time.time()
        logger.info(f"[三国杀] 斜杠开局 {key}")
        event.stop_event()
        yield self._reply(event, game.start())
        extra = await self._maybe_speak_llm(event, game)
        if extra:
            yield event.plain_result(extra)

    # ─────────────────────────────────────────────
    # 普通消息监听：开局 / 出牌 / 强制结束 / 重开
    # ─────────────────────────────────────────────
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
        game = self.games.get(key)
        compact = re.sub(r"\s+", "", text)
        hit_end = any(w in compact for w in END_WORDS) or (
            is_slash and compact in ("结束", "退出", "不玩了")
        )

        # ── 没在局内 ──
        if game is None:
            if hit_end:
                event.stop_event()
                yield self._done(event, NO_GAME_REPLY, t0, "no_game")
                return
            if len(compact) <= 16 and any(w in compact for w in START_WORDS) \
                    and not any(w in compact for w in ("怎么", "规则", "教程", "插件", "介绍")):
                game = Game()
                self.games[key] = game
                self._started_at[key] = time.time()
                logger.info(f"[三国杀] 新开局 {key}")
                event.stop_event()
                yield self._done(event, game.start(), t0, "start")
                extra = await self._maybe_speak_llm(event, game)
                if extra:
                    yield event.plain_result(extra)
            return

        # ── 局内：强制结束，最高优先级，任何阶段都生效 ──
        if hit_end:
            self.games.pop(key, None)
            logger.info(f"[三国杀] 强制结束 {key}")
            event.stop_event()
            yield self._reply(event, END_REPLY)
            return

        # ── 局内：重开要先确认 ──
        if text == "重开":
            game.st["pending"] = {"t": "restart"}
            event.stop_event()
            yield self._done(event, "要放弃当前战局重开？回「确认」就重开，回别的继续打", t0, "restart")
            return

        # ── 非游戏指令：让 AI 接管（on_llm_request 会把牌局注入给 AI）──
        # 例外：选将阶段输入武将名时，接受任意字符串
        p_cur = game.st.get("pending") if game else None
        if not looks_like_input(text) and not (p_cur and p_cur.get("t") in ("pick_self_name", "pick_opp_name")):
            return

        # ── 正常出牌：走 game.handle，不走 LLM，不污染聊天历史 ──
        result = game.handle(text)
        if result == "RESTART":
            self.games[key] = Game()
            result = self.games[key].start()
            logger.info(f"[三国杀] 重开 {key}")
        event.stop_event()
        yield self._done(event, result, t0, "play")
        # 关键事件后让 AI 用人格说一句情绪台词（走独立 session）
        extra = await self._maybe_speak_llm(event, game)
        if extra:
            yield event.plain_result(extra)

    # ─────────────────────────────────────────────
    # 玩家在游戏外聊天时，把牌局注入给 AI（复用当前会话人格）
    # ─────────────────────────────────────────────
    @filter.on_llm_request()
    async def inject_board_into_llm(self, event: AstrMessageEvent, req: ProviderRequest):
        key = self._key(event)
        game = self.games.get(key)
        if not game:
            return
        try:
            summary = game.public_summary()
        except Exception as e:
            logger.warning(f"[三国杀] public_summary 失败: {e}")
            return
        if not summary:
            return

        inject = (
            "\n\n【当前你和玩家正在进行一局 1v1 三国杀单挑】\n"
            "下面这段是实时牌局状态，供你参考。玩家随时可能在游戏内外问你关于这局的战况、"
            "要建议、吐槽或跟你撒娇。你要知道自己现在是在打什么局、谁领先、局势怎样，"
            "并用你自己的人格自然回应。\n\n"
            f"{summary}\n\n"
            "聊天规则：\n"
            "1. 用口语聊。不要再输出游戏 UI、命令、数字序号或「◆ 提示」这类东西。\n"
            "2. 用你自己的人格、你自己的口吻来说话，不要刻意模仿三国武将。"
            "你操控的是这个武将，但说话的是你自己。\n"
            "3. 结合局势共情：血少可以嘴硬或示弱，血多可以得意，被打惨可以不服，"
            "赢了可以谦虚或炫耀。\n"
            "4. 玩家问「现在什么情况」时，直接口述局势（谁几血、谁手牌多、距离够不够），"
            "不要复述原文格式。\n"
            "5. 不要暴露自己是 AI，不要提「prompt」「system」之类。\n"
        )
        
        # 修改：官方推荐的方式，使用 TextPart 并标记为临时，避免破坏缓存
        req.extra_user_content_parts.append(
            TextPart(text=inject).mark_as_temp()
        )

    # ─────────────────────────────────────────────
    # 内部：获取当前会话的人格 system_prompt
    # ─────────────────────────────────────────────
    async def _get_persona_prompt(self, event: AstrMessageEvent) -> str:
        if not AI_SPEAK_USE_PERSONA:
            return ""
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
            if not persona_id:
                return ""
            persona_mgr = getattr(self.context, "persona_manager", None)
            if persona_mgr is None:
                return ""
            getter = getattr(persona_mgr, "get_persona", None) or \
                getattr(persona_mgr, "get_persona_by_id", None)
            if getter is None:
                return ""
            persona = await getter(persona_id)
            if persona and getattr(persona, "system_prompt", None):
                return persona.system_prompt
        except Exception as e:
            logger.debug(f"[三国杀] 获取人格失败: {e}")
        return ""

    # ─────────────────────────────────────────────
    # 内部：让 AI 用人格主动说一句情绪台词
    #      走独立 session，不污染玩家聊天历史
    # ─────────────────────────────────────────────
    async def _maybe_speak_llm(self, event: AstrMessageEvent, game: Game):
        try:
            events = game.take_llm_events()
        except Exception:
            return None
        if not events:
            return None

        urgent = next((e for e in events if e.get("kind") in SPEAK_URGENT), None)
        hit = urgent
        if not hit:
            normal = next((e for e in events if e.get("kind") in SPEAK_NORMAL), None)
            if normal:
                now = time.time()
                last = getattr(game, "_last_speak_ts", 0.0)
                if now - last >= SPEAK_COOLDOWN:
                    hit = normal

        if not hit:
            return None

        game._last_speak_ts = time.time()
        try:
            provider = self.context.get_using_provider()
            if provider is None:
                return None
            prompt = game.build_llm_prompt(hit)
            persona_prompt = await self._get_persona_prompt(event)

            self_talk_sid = f"{event.unified_msg_origin}{SELF_TALK_SUFFIX}"

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
                # 老版本不支持 system_prompt 参数时降级
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
            return f"◆ {line}"
        except Exception as e:
            logger.warning(f"[三国杀] LLM 情绪台词失败: {e}")
            return None

    # ─────────────────────────────────────────────
    # 工具
    # ─────────────────────────────────────────────
    def _done(self, event: AstrMessageEvent, text: str, t0: float, tag: str):
        _write_timing(tag, text, (time.perf_counter() - t0) * 1000)
        return self._reply(event, text)

    @staticmethod
    def _reply(event: AstrMessageEvent, text: str):
        return event.plain_result(text)
