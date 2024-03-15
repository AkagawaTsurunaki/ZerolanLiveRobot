import time
from dataclasses import dataclass
from typing import List

from javascript import require, On
from loguru import logger

mineflayer = require('mineflayer', 'latest')
Vec3 = require('vec3').Vec3

MINECRAFT_SERVER_HOST = 'localhost'
MINECRAFT_SERVER_PORT = 25565
MINECRAFT_BOT_NAME = 'Koneko'

bot = mineflayer.createBot({
    "host": MINECRAFT_SERVER_HOST,
    "port": MINECRAFT_SERVER_PORT,
    "username": MINECRAFT_BOT_NAME,
})


# Item = require("prismarine-item")(bot.registry)

@dataclass
class GameEvent:
    read: bool
    time_stamp: float
    health: int
    food: int
    environment: str | None


game_event_list: List[GameEvent] = []


def select():
    if len(game_event_list) > 0:
        event = game_event_list[-1]
        if not event.read:
            event.read = True
            return event
    return None


def create_game_event(env: str):
    return GameEvent(time_stamp=time.time(), health=bot.health, food=bot.food, environment=env, read=False)


# @On(bot, 'entityHurt')
# def handle(this, entity, *args):
#     logger.info('cesghu')
#     if entity.name == MINECRAFT_BOT_NAME:
#         game_event = create_game_event()
#         game_event.environment = '你受伤了'
#         bot.chat('受伤了')
#         logger.info('受伤')
g_bot_entity_id = None


def add(event: GameEvent):
    game_event_list.append(event)


@On(bot, 'spawn')
def handle_spawn(this):
    global g_bot_entity_id
    if bot:
        g_bot_entity_id = bot.entity.id


@On(bot, "chat")
def handle(this, username, message, *args):
    logger.info(f'{username} {message}')


def bot_hurt():
    logger.info('被攻击了')
    event = create_game_event(env='注意！你被攻击了！')
    add(event)


@On(bot._client, 'damage_event')
def handle_damage_event(this, packet, *args):
    logger.info(packet)
    entity_id, source_type_id, source_cause_id, source_direct_id = packet.values()
    if g_bot_entity_id:
        if g_bot_entity_id == entity_id:
            bot_hurt()


@On(bot, 'death')
def death_handle(this, *args):
    logger.info(f'你死了')
    event = create_game_event(env='注意！你已经死亡了！')
    add(event)
