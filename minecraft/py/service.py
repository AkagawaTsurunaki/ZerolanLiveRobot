import json
from dataclasses import asdict
from typing import List

from javascript import require, On, Once

from minecraft.py.body import bot_hurt, bot_death, check_health_changed, check_food_changed, reset_body_info
from minecraft.py.common import create_game_event, GameEvent
from minecraft.py.eater import auto_eat
from minecraft.py.guard import attack_mobs

mineflayer = require('mineflayer', 'latest')
autoeat = require('mineflayer-auto-eat')
pvp = require('mineflayer-pvp')
pathfinder = require('mineflayer-pathfinder')
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
# PVP 插件
bot.loadPlugin(pathfinder.pathfinder)
bot.loadPlugin(pvp.plugin)

game_event_list: List[GameEvent] = []


def bot_log(msg):
    bot.chat(msg)


def select():
    if len(game_event_list) > 0:
        event = game_event_list[-1]
        if not event.read:
            event.read = True
            return event
    return None


def add_event(event: GameEvent):
    if event:
        game_event_list.append(event)
        bot_log(f'游戏事件 {json.dumps(obj=asdict(event), indent=4, ensure_ascii=False)}')


@Once(bot, 'spawn')
def handle_once_spawn(this):
    bot.autoEat.options = {
        "priority": 'foodPoints',
        "startAt": 14,
        "bannedFood": []
    }


@On(bot, 'physicsTick')
def handle_in_physics_ticks(this):
    try:
        add_event(check_health_changed(bot))
        add_event(check_food_changed(bot))
        attack_mobs(bot)
    except Exception as e:
        print(e)


@On(bot, 'spawn')
def handle_spawn(this):
    reset_body_info()
    add_event(create_game_event(bot=bot, env='你重生了'))


@On(bot, "chat")
def handle(this, username, message, *args):
    ...


@On(bot, 'health')
def handle_health(this):
    auto_eat_event = auto_eat(bot)
    add_event(auto_eat_event)


@On(bot._client, 'damage_event')
def handle_damage_event(this, packet, *args):
    entity_id, source_type_id, source_cause_id, source_direct_id = packet.values()
    bot_hurt_event = bot_hurt(bot, entity_id)
    add_event(bot_hurt_event)


@On(bot, 'death')
def death_handle(this, *args):
    bot_death_event = bot_death(bot)
    add_event(bot_death_event)
