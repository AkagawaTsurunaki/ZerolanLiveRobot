import {pathfinder} from "mineflayer-pathfinder";
import {createBot} from "mineflayer";
import {plugin as autoeat} from "mineflayer-auto-eat"
import "mineflayer"
import {fertilize, harvest, sow} from "./farmer"
import {plugin as pvp} from "mineflayer-pvp";
import {findNearestPlayer, moveToPos} from "./util";
import {attackMobs} from "./attack";
import {faceMe, followMe} from "./follow";

export const bot = createBot({
    host: 'localhost',
    port: 25565,
    username: 'Koneko'
})

bot.loadPlugin(pathfinder)
bot.loadPlugin(pvp)
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
// @ts-ignore
bot.on("stoppedAttacking", () => {
    const nearestPlayer = findNearestPlayer(bot, 5, 50)
    if (nearestPlayer) {
        moveToPos(bot, nearestPlayer.position)
    }
})
var fun = 0
bot.on('physicsTick', async () => {
    await attackMobs(bot)
    fun++;
    console.log(fun)
    if (fun % 20 == 0 ) {
        followMe(bot)
    }
})

bot.on('chat', async (username, message, translate, jsonMsg, matches) => {
    if (['来', 'lai', 'come'].includes(message)) {
        followMe(bot)
    } else if (['种', 'zhong', 'sow'].includes(message)) {
        await sow(bot)
    } else if (['收', 'shou', 'harvest'].includes(message)) {
        await harvest(bot)
    } else if (['施肥', 'shifei', 'fertilize'].includes(message)) {
        await fertilize(bot)
    }
})

bot.on('hardcodedSoundEffectHeard', async (soundId, soundCategory, position, volume, pitch) => {
    await faceMe(bot, position, soundCategory)
})

bot.on('health', () => {
    bot.chat(`被攻击了 ${bot.health}`)
})

