import asyncio
import os
import random
import time
from typing import Union

from agent.api import rank_essence_messages
from common.collection.limit_list import LimitList
from common.io.file_sys import fs
from services.qqbot.util import _essence_msg_to_json

_napcat_dir = fs.temp_dir.joinpath('napcat')


def _set_napcat_env():
    # Prevent ncatbot from creating default directories directly in the project directory.
    # WebUI, plugins are disabled.
    _napcat_dir.mkdir(parents=True, exist_ok=True)
    napcat_log_dir = _napcat_dir.joinpath('logs')
    napcat_log_dir.mkdir(parents=True, exist_ok=True)
    napcat_plugin_dir = _napcat_dir.joinpath('plugins')
    napcat_plugin_dir.mkdir(parents=True, exist_ok=True)
    os.environ['NCATBOT_CONFIG_PATH'] = str(_napcat_dir.joinpath('config.yaml'))
    os.environ['LOG_FILE_PATH'] = str(napcat_log_dir)

    from ncatbot.utils import ncatbot_config
    ncatbot_config.napcat.enable_webui = False
    ncatbot_config.plugin.skip_plugin_load = True
    ncatbot_config.plugin.plugins_dir = str(napcat_plugin_dir)


# Note: Do not import any `ncatbot` modules before `_set_napcat_env()` is called.
_set_napcat_env()

from loguru import logger
from ncatbot.core import BotClient, GroupMessageEvent, PrivateMessageEvent, MessageArray

from typeguard import typechecked

from event.event_data import QQMessageEvent
from event.event_emitter import emitter
from services.qqbot.config import QQBotServiceConfig


class QQBotService:
    def __init__(self, config: QQBotServiceConfig):

        self._bot = BotClient()
        self._api = self._bot.run_backend(bt_uin=config.qq_num, ws_uri=config.ws_uri,
                                          ws_token=config.ws_token, debug=False)
        self._root_user = config.root
        self._self_qq = config.qq_num
        self._groups = config.groups if config.groups is not None else []
        logger.info("QQ bot started with Napcat backend.")

        # 自由发言机制
        self._last_sent_time = time.time()
        self._sent_interval = 120  # 间隔多长时间才被允许重新发言
        self._free_talk_in_group = True

        # 自动设精机制
        self._single_img_only: bool = True  # 是否只取一条消息中的一张图片
        self._auto_set_essence_msg = True  # 自动设精 :)
        self._prob_set_essence_msg = 2  # 设精概率，大于 1 表示不设概率限制
        self._thr_set_essence_msg = 99  # 设精阈值，模型根据对话打分，超过该阈值的认为是精华消息
        self._trigger_num_history = 2  # 多少条记录触发模型的精华消息检查
        self._max_history = 5  # 群内记录的最大条数是多少，可认为是窗口大小
        self._history = {}

        # at 发言机制
        self._at_reply = True # 是否立刻回复 at 你的人

        self._essence_dir = _napcat_dir.joinpath('essence')
        self._essence_dir.mkdir(parents=True, exist_ok=True)

        self._init()

    def _init(self):
        @self._bot.on_group_message()
        async def echo_cmd(event: GroupMessageEvent):
            if str(event.sender.user_id) != str(self._root_user):
                return
            text = "".join(seg.text for seg in event.message.filter_text())
            if "echo" in text:
                if self.can_send():
                    await event.reply(text[4:])
                    self.set_timer()

        @self._bot.on_group_message()
        async def emit_plain_text_msg(event: GroupMessageEvent):
            if not (event.group_id in self._groups):
                return
            text = "".join(seg.text for seg in event.message.filter_text())
            images = event.message.filter_image()
            logger.debug(f"Received QQ message: {text}")
            if self._free_talk_in_group and self.can_send():
                await self._emit_qq_msg(images, text, sender_id=str(event.sender.user_id), group_id=str(event.group_id))
                self.set_timer()

            if self._at_reply and self._is_at_me(event.message):
                await self._emit_qq_msg(images, text, sender_id=str(event.sender.user_id), group_id=str(event.group_id))

            await self.attempt_add_essence_msg(group_id=event.group_id, sender_id=event.sender.user_id,
                                               text=text, msg_id=event.message_id)

        @self._bot.on_private_message()
        async def on_private_message(event: PrivateMessageEvent):
            if str(event.sender.user_id) != str(self._root_user):
                return
            text = "".join(seg.text for seg in event.message.filter_text())
            images = event.message.filter_image()
            logger.debug(f"Received private QQ message: {text}")
            if '/导出精华' in text:
                subactions = text.split(' ')
                if len(subactions) == 2:
                    group_id = subactions[1]
                    await self._export_essence_messages_by_group(group_id)
                else:
                    self.send_plain_message(group_id=None, receiver_id=event.sender.user_id,
                                            text='指令格式错误：/导出精华 <群ID>')
            elif '/清除精华' in text:
                subactions = text.split(' ')
                if len(subactions) == 2:
                    group_id = subactions[1]
                    await self._remove_essence_messages_by_group(group_id)
                else:
                    self.send_plain_message(group_id=None, receiver_id=event.sender.user_id,
                                            text='指令格式错误：/清除精华 <群ID>')
            else:
                await self._emit_qq_msg(images, text, sender_id=str(event.sender.user_id), group_id=None)

    def _is_at_me(self, msg_arr: MessageArray):
        ats = msg_arr.filter_at()
        for at in ats:
            if at.qq == self._self_qq:
                return True
        return False

    async def attempt_add_essence_msg(self, group_id: Union[str, int], sender_id: Union[str, int],
                                      text: str, msg_id: Union[str, int]):
        if group_id not in self._history.keys():
            self._history[group_id] = LimitList(self._max_history)
            history = self._history[group_id]
            history.append(
                {
                    "user_id": str(sender_id),
                    "msg": text,
                    'msg_id': str(msg_id),
                    "essence_score": 0
                }
            )

            if len(history) >= self._trigger_num_history:
                if self._prob_set_essence_msg > random.random():
                    conversations = [item['msg'] for item in history]
                    cand_msgs = rank_essence_messages(conversations)
                    cand_msgs.sort(key=lambda x: x[1], reverse=True)
                    essence_msg_indices = [msg[0] for msg in cand_msgs if msg[1] > self._thr_set_essence_msg]
                    logger.info(f'Essence messages are checked: Indices are {essence_msg_indices}.')
                    if len(essence_msg_indices) >= 1:
                        await self._bot.api.setessence(essence_msg_indices[0])
                    else:
                        logger.info(f"Skip due to partial detection of essence messages")

    async def _export_essence_messages_by_group(self, group_id: Union[str, int]):
        jsonl_path = self._essence_dir.joinpath(f'{group_id}-{time.time()}.jsonl')
        with open(jsonl_path, mode='w+', encoding='utf-8') as f:
            logger.info(f'Saving essence messages from group {group_id}...')
            emsg_list = await self._bot.api.get_essence_msg_list(group_id)
            for emsg in emsg_list:
                emsg_json_line = _essence_msg_to_json(emsg)
                logger.debug(emsg_json_line)
                f.write(emsg_json_line + '\n')

    async def _remove_essence_messages_by_group(self, group_id: Union[str, int]):
        emsg_list = await self._bot.api.get_essence_msg_list(group_id)
        for emsg in emsg_list:
            await self._bot.api.delete_essence_msg(emsg.message_id)
            emsg_json_line = _essence_msg_to_json(emsg)
            logger.debug(f'Remove essence message: {emsg_json_line}')
            await asyncio.sleep(1)

    async def _emit_qq_msg(self, images, text, sender_id: str | None, group_id: str | None):
        if len(images) > 0:
            if self._single_img_only:
                image = images[0]
                img_path = fs.create_temp_file_descriptor(prefix='qqbot', suffix='.jpg', type='image')
                save_dir, filename = os.path.split(img_path)
                await image.download(save_dir, filename)
                if img_path.exists():
                    logger.debug(f"Received QQ image message: {img_path}")
                    emitter.emit(QQMessageEvent(message=text,
                                                images=[img_path],
                                                group_id=group_id,
                                                sender_id=sender_id))
            else:
                logger.warning("Not implemented.")
        else:
            emitter.emit(QQMessageEvent(message=text,
                                        group_id=group_id,
                                        sender_id=sender_id))

    def set_timer(self):
        self._last_sent_time = time.time()

    def can_send(self):
        now = time.time()
        print(now - self._last_sent_time)
        if now - self._last_sent_time > self._sent_interval:
            return True
        logger.warning("Limit sending QQ message.")
        return False

    @typechecked
    def send_plain_message(self, group_id: str | None, receiver_id: str | None, text: str):
        assert receiver_id is not None or group_id is not None
        if group_id is not None:
            self._api.send_group_text_sync(group_id=group_id, text=text)
        else:
            self._api.send_private_plain_text_sync(user_id=receiver_id, text=text)
        logger.info(f"Sent QQ message: {text}")

    @typechecked
    def send_speech(self, group_id: str, audio_path: str):
        assert os.path.exists(audio_path)
        self._api.send_group_record_sync(group_id, audio_path)

    def start(self):
        # self._api.send_private_text_sync(self._root_user, "hello")
        # self._bot.start()
        pass

    def stop(self):
        self._bot.bot_exit()
