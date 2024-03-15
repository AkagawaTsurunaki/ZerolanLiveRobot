const mineflayer = require('mineflayer')
const options = {
    host: 'localhost', // Change this to the ip you want.
    port: 25565,// Change this to the port you want.
    username: 'Koneko',
    version: '1.20.4'
}
const bot = mineflayer.createBot(options)
const welcome = () => {
    bot.chat('主人好喵~')
}

async function consume(bot) {
    try {
        await bot.consume()
        console.log('Finished consuming')
    } catch (err) {
        console.log(err)
    }
}

// console.log(bot)
console.log(bot.food)
bot.once('heldItemChanged', () => {
    consume(bot)
})
// consume(bot).then(r => {})



