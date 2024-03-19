import {pathfinder} from "mineflayer-pathfinder";
import {createBot} from "mineflayer";
import {plugin as autoeat} from "mineflayer-auto-eat"
import "mineflayer"
import {fertilize, harvest, sow} from "./farmer"
import {plugin as pvp} from "mineflayer-pvp";
import {addRespawnEvent, findNearestPlayer, moveToPos} from "./util";
import {attackMobs} from "./attack";
import {faceMe, followMe, wander} from "./follow";
import {botHurt} from "./body";

export const bot = createBot({
    host: 'localhost',
    port: 25565,
    username: 'Koneko'
})

bot.loadPlugin(pathfinder)
bot.loadPlugin(pvp)
bot.loadPlugin(autoeat)

bot.once('spawn', async () => {
    // @ts-ignore
    bot.autoEat.options = {
        priority: 'foodPoints',
        startAt: 14,
        bannedFood: []
    }
})

bot.on('respawn', async () => {
    await addRespawnEvent(bot)
})

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

bot._client.on('damage_event', async (packet) => {
    const entityId = packet.entityId
    const sourceTypeId = packet.sourceTypeId
    const sourceCauseId = packet.sourceCauseId
    const sourceDirectId = packet.sourceDirectId
    await botHurt(bot, entityId)
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
    // const gev = new GameEvent(bot, '你好')
    // postGameEvent(gev)
    await attackMobs(bot)
    fun++;
    if (fun % 20 == 0) {
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
    } else if (['玩', 'wan', 'play'].includes(message)) {
        await wander(bot)
    }
})

bot.on('hardcodedSoundEffectHeard', async (soundId, soundCategory, position, volume, pitch) => {
    await faceMe(bot, position, soundCategory)
})
