import {pathfinder} from "mineflayer-pathfinder";
import {createBot} from "mineflayer";
import {plugin as autoeat} from "mineflayer-auto-eat"
import "mineflayer"
import {sow} from "./farmer"
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


// @ts-ignore
bot.on("stoppedAttacking", () => {
    const nearestPlayer = findNearestPlayer(bot, 5, 50)
    if (nearestPlayer) {
        moveToPos(bot, nearestPlayer.position)
    }
})

bot.on('physicsTick', async () => {
    await attackMobs(bot)
})

bot.on('chat', async (username, message, translate, jsonMsg, matches) => {
    if (['来', 'lai', 'come'].includes(message)) {
        followMe(bot)
    } else if (['种', 'zhong', 'sow'].includes(message)) {
        sow(bot)
    }
})

bot.on('hardcodedSoundEffectHeard', async (soundId, soundCategory, position, volume, pitch) => {
    await faceMe(bot, position, soundCategory)
})

bot.on('health', () => {
    bot.chat(`被攻击了 ${bot.health}`)
})

