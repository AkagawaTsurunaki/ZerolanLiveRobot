def attack_mobs(bot):
    if bot:
        bot_pos = bot.entity.position

        def mob_filter(e):
            return e.type == 'hostile' and e.position.distanceTo(bot_pos) < 8

        entity = bot.nearestEntity(mob_filter)
        if entity:
            bot.pvp.attack(entity)
