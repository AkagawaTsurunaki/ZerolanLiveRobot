/**
 * 当听到僵尸的叫声后, 将头朝向声源, 如果僵尸在16格以内, 则进行攻击
 */

if (process.argv.length < 4 || process.argv.length > 6) {
    console.log('Usage : node guard.js <host> <port> [<name>] [<password>]')
    process.exit(1)
}

const mineflayer = require('mineflayer')
const {pathfinder, Movements, goals} = require('mineflayer-pathfinder')
const pvp = require('mineflayer-pvp').plugin

const bot = mineflayer.createBot({
    host: process.argv[2],
    port: parseInt(process.argv[3]),
    username: process.argv[4] ? process.argv[4] : 'Guard',
    password: process.argv[5]
})

bot.on('spawn', () => {
    setTimeout(() => {
        bot.chat('Ciallo～(∠・ω< )⌒★ 主人好喵!')
    }, 3000)
})


bot.on('physicsTick', async () => {
    //  (e.displayName === 'Zombie' || e.displayName === 'Akagawa') &&
    const mobFilter = e => (e.displayName === 'Zombie' || e.type === 'player') && e.position.distanceTo(bot.entity.position) < 3
    const entity = bot.nearestEntity(mobFilter)
    if (entity) {
        bot.attack(entity)
    }
})
bot.on('hardcodedSoundEffectHeard', async (soundId, soundCategory, position, volume, pitch) => {
    console.log(`${soundId}`)
    if (soundId === 1517 || soundId === 1527 || soundId === 251) {
        bot.lookAt(position)
    }
})
// bot.on('soundEffectHeard', async (soundName, position, volume, pitch) => {
//   console.log(`${soundName}`)
// })
//
// bot.on('hardcodedSoundEffectHeard', async (soundId, soundCategory, position, volume, pitch) => {
//   console.log(`${soundId}`)
// })


// bot.on('soundEffectHeard', async (soundName, position, volume, pitch) => {
//     console.log('test')
//     // console.log(soundName)
//     if (soundName === 'entity.zombie.ambient') {
//         bot.lookAt(position).then(r => {
//             bot.chat('I heard a zombie.')
//             const filter = e => e.type === 'mob' && e.position.distanceTo(bot.entity.position) < 16 &&
//                 e.displayName !== 'Armor Stand' // Mojang classifies armor stands as mobs for some reason?
//
//             const mobEntities = bot.entities(filter)
//             const zombieFilter = e => e.type === 'mob' && e.displayName === 'Zombie'
//             zombies = mobEntities(zombieFilter)
//             const entity = bot.nearestEntity(zombies)
//             if (entity) {
//                 bot.pvp.attack(entity)
//             }
//         })
//
//     }
//
// })

// bot.on('physicsTick', () => {
//     // 只有当听到mob叫声时
//     console.log('test')
//
// })
