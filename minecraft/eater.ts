import {bot} from "./service"
import {plugin as autoeat} from "mineflayer-auto-eat";

// Load the plugin
bot.loadPlugin(autoeat)

bot.once('spawn', () => {
    // @ts-ignore
    bot.autoEat.options = {
        priority: 'foodPoints',
        startAt: 14,
        bannedFood: []
    }
})
// The bot eats food automatically and emits these events when it starts eating and stops eating.

bot.on('autoeat_started', () => {
    console.log('Auto Eat started!')
})

bot.on('autoeat_finished', () => {
    console.log('Auto Eat stopped!')
})

bot.on('health', () => {
    if (bot.food === 20) bot.autoEat.disable()
    // Disable the plugin if the bot is at 20 food points
    else bot.autoEat.enable() // Else enable the plugin again
})