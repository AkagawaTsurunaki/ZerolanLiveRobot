def auto_eat(bot):
    if bot.food == 20:
        bot.autoEat.disable()
    else:
        bot.autoEat.enable()
