import time
from dataclasses import dataclass
from typing import List

from javascript import require, On, Once
from loguru import logger

mineflayer = require('mineflayer', 'latest')
autoeat = require('mineflayer-auto-eat')
Vec3 = require('vec3').Vec3

MINECRAFT_SERVER_HOST = 'localhost'
MINECRAFT_SERVER_PORT = 25565
MINECRAFT_BOT_NAME = 'Koneko'

bot = mineflayer.createBot({
    "host": MINECRAFT_SERVER_HOST,
    "port": MINECRAFT_SERVER_PORT,
    "username": MINECRAFT_BOT_NAME,
})
# 自动进食
bot.loadPlugin(autoeat.plugin)

# 机器人的实体 ID
g_bot_entity_id = None


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


def add(event: GameEvent):
    game_event_list.append(event)

def bot_chat(msg):
    bot.chat(msg)


@Once(bot, 'spawn')
def handle_once_spawn(this):
    bot.autoEat.options = {
        "priority": 'foodPoints',
        "startAt": 14,
        "bannedFood": []
    }


@On(bot, 'spawn')
def handle_spawn(this):
    global g_bot_entity_id
    if bot:
        g_bot_entity_id = bot.entity.id
        add(create_game_event(env='你重生了'))


@On(bot, "chat")
def handle(this, username, message, *args):
    logger.info(f'{username} {message}')


@On(bot, 'health')
def handle_health(this):
    if bot.food == 20:
        bot.autoEat.disable()
    else:
        bot.autoEat.enable()


def bot_hurt():
    event = create_game_event(env='注意！你被攻击了！')
    add(event)


@On(bot._client, 'damage_event')
def handle_damage_event(this, packet, *args):
    entity_id, source_type_id, source_cause_id, source_direct_id = packet.values()
    if g_bot_entity_id:
        if g_bot_entity_id == entity_id:
            bot_hurt()


@On(bot, 'death')
def death_handle(this, *args):
    event = create_game_event(env='注意！你已经死亡了！')
    add(event)
