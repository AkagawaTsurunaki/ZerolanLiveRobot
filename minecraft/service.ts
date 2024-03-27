import {pathfinder} from "mineflayer-pathfinder";
import {createBot} from "mineflayer";
import {plugin as autoeat} from "mineflayer-auto-eat"
import "mineflayer"
import {fertilize, harvest, sow} from "./skill/farm"
import {plugin as pvp} from "mineflayer-pvp";
import {findNearestPlayer, moveToPos} from "./util";
import {attackMobs} from "./skill/attack";
import {faceMe, followMe, wander} from "./skill/follow";
import {botHurt, botInterrupt} from "./body";
import {propitiate, tickCheckAngry} from "./brain/angry"
import {emitRespawnEvent} from "./event";
import {Entity} from "prismarine-entity";
import {fightingWithHostiles} from "./brain/intent";

const options = {
    host: process.argv[2],
    port: parseInt(process.argv[3]),
    username: process.argv[4],
    password: process.argv[5]
}

const bot = createBot(options)

console.log(`玩家 ${options.username} 成功登录 ${options.host}:${options.port}`)

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
    await emitRespawnEvent(bot)
})

bot.on('autoeat_started', () => {
})

bot.on('autoeat_finished', () => {
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
    botHurt(bot, entityId, sourceTypeId, sourceCauseId, sourceDirectId)
    botInterrupt(bot, entityId, sourceTypeId, sourceCauseId, sourceDirectId)
})

// @ts-ignore
bot.on("stoppedAttacking", () => {
    fightingWithHostiles.clear()
    const nearestPlayer = findNearestPlayer(bot, 5, 50)
    if (nearestPlayer) {
        moveToPos(bot, nearestPlayer.position)
    }
})
var fun = 0
bot.on('physicsTick', async () => {
    await attackMobs(bot)
    fun++;
    if (fun % 20 == 0) {
        followMe(bot)
    }
    await tickCheckAngry(bot)
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

bot.on('diggingAborted', (block) => {
    block.position
})

bot.on('hardcodedSoundEffectHeard', async (soundId, soundCategory, position, volume, pitch) => {
    await faceMe(bot, position, soundCategory)
})

// @ts-ignore
bot.on('attackedTarget', () => {
    propitiate(30)
})


// @ts-ignore
bot.on('blockBreakProgressEnd', async (block: Block, entity: Entity) => {
    // console.log(entity.position)
    if (entity.type === 'player') {
        moveToPos(bot, block.position.offset(0, 1, 0))
        await bot.lookAt(entity.position)
    }
})