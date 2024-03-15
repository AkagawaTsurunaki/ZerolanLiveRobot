const mineflayer = require('mineflayer')
const {pathfinder, Movements, goals} = require('mineflayer-pathfinder')
const pvp = require('mineflayer-pvp').plugin

const { sow } = require('./farmer')

const bot = mineflayer.createBot({
    host: 'localhost',
    port: 25565,
    username: 'Koneko'
})

bot.loadPlugin(pathfinder)
bot.loadPlugin(pvp)

// /**
//  * 寻找最近的玩家
//  * @param min_dist 最小搜索半径
//  * @param max_dist 最大搜索半径
//  * @returns {Entity|null}
//  */
// const findNearestPlayer = (min_dist = 0, max_dist = 255) => {
//     let player_filter = e => e.type === 'player'
//     player = bot.nearestEntity(player_filter)
//     dist = player.position.distanceTo(bot.entity.position)
//     if (min_dist < dist && dist < max_dist) {
//         return player
//     }
//     return null
// }
//
// // Pathfinder to the guard position
// function moveTo(pos) {
//     bot.pathfinder.setMovements(new Movements(bot))
//     bot.pathfinder.setGoal(new goals.GoalBlock(pos.x, pos.y, pos.z))
// }
//
// // 装备不死图腾
// const auto_totem = () => {
//     const totemId = bot.registry.itemsByName.totem_of_undying.id // Get the correct id
//     if (bot.registry.itemsByName.totem_of_undying) {
//         setInterval(() => {
//             const totem = bot.inventory.findInventoryItem(totemId, null)
//             if (totem) {
//                 bot.equip(totem, 'off-hand')
//             }
//         }, 50)
//     }
// }

bot.on('stoppedAttacking', () => {
    const nearestPlayer = findNearestPlayer(5, 50)
    if (nearestPlayer) {
        moveTo(nearestPlayer.position)
    }
})


bot.on('physicsTick', async () => {
    const mobFilter = e => e.type === 'hostile' && e.position.distanceTo(bot.entity.position) < 8
    const entity = bot.nearestEntity(mobFilter)
    if (entity) {
        await bot.pvp.attack(entity)
    }
})

// 招呼Bot的命令短语
comeHereCmd = [
    "来我这",
    "请过来",
    "来啊",
    "过来",
    "过来一下",
    "过来一下啊",
    "到这边来",
    "走过来",
    "跟我来",
    "快过来",
    "快点过来",
    "过来吧",
    "赶紧过来",
    "过来一下吧",
    "过来一下呀",
    "过来一下哦",
    "过来看看",
    "过来一趟",
    "向我靠近",
    "朝这边走",
    "朝这里走",
    "朝着这边来",
    "朝着这里来",
    "这边过来",
    "这里过来",
    "这边过来一下",
    "这里过来一下",
    "这边来一下",
    "这里来一下",
    "这里看看",
    "这边看看",
    "这里过来看看",
    "这边过来看看",
    "这里过来一趟",
    "这边过来一趟",
    "过来这里",
    "过来这边",
    "跟我来",
    "follow me",
    "Follow me",
    "Come here"
]
bot.on('chat', async (username, message, translate, jsonMsg, matches) => {
    if (comeHereCmd.includes(message)) {
        bot.chat('好的喵, 主人!')
        const player_filter = e => e.type === 'player' && e.position.distanceTo(bot.entity.position) > 5
        player_entity = bot.nearestEntity(player_filter)
        moveTo(player_entity.position)
    } else if (message === '种') {
        sow(bot)
    }
})

bot.on('hardcodedSoundEffectHeard', async (soundId, soundCategory, position, volume, pitch) => {
    distance = bot.entity.position.distanceTo(position)
    if (soundCategory === 'player') {
        if (1 < distance && distance < 20) {
            bot.lookAt(position)
        }
    } else if (soundCategory === 'hostile') {
        if (distance < 20) {
            bot.lookAt(position)
        }
    }
})

bot.on('health', () => {
    bot.chat(`被攻击了 ${bot.health}`)
})
