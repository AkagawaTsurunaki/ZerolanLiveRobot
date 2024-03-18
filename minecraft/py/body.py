from math import floor

from minecraft.py.common import create_game_event

bot_current_health = -1
bot_current_food = -1


def reset_body_info():
    global bot_current_food, bot_current_health
    bot_current_health = -1
    bot_current_food = - 1


def check_health_changed(bot):
    if bot:
        global bot_current_health
        if bot_current_health < 0:
            bot_current_health = floor(bot.health)
            return None
        if bot_current_health < floor(bot.health):
            offset = floor(bot.health) - bot_current_health
            bot_current_health = floor(bot.health)
            return create_game_event(bot, f'你恢复了 {offset} 点生命值。')
        elif bot_current_health > floor(bot.health):
            offset = bot_current_health - floor(bot.health)
            bot_current_health = floor(bot.health)
            return create_game_event(bot, f'你失去了 {offset} 点生命值。')
        else:
            return None
    return None


def check_food_changed(bot):
    if bot:
        global bot_current_food
        if bot_current_food < 0:
            bot_current_food = int(bot.food)
            return None
        if bot_current_food < int(bot.food):
            offset = int(bot.food) - bot_current_food
            bot_current_food = int(bot.food)
            return create_game_event(bot, f'你吃了一些东西：恢复了 {offset} 点体力值。')
        elif bot_current_food > int(bot.food):
            offset = bot_current_food - int(bot.food)
            bot_current_food = int(bot.food)
            return create_game_event(bot, f'你有点饿了：失去了 {offset} 点体力值。')
        else:
            return None
    return None


def bot_hurt(bot, entity_id):
    if bot and entity_id:
        if bot.entity.id == entity_id:
            event = create_game_event(bot=bot, env='注意！你被攻击了！')
            return event
    return None


def bot_death(bot):
    if bot:
        event = create_game_event(bot=bot, env='注意！你已经死亡了！即将开始新的一次探险！')
        return event
    return None
