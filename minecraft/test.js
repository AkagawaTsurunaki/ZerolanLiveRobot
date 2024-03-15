const mineflayer = require('mineflayer')
const options = {
    host: 'localhost', // Change this to the ip you want.
    port: 25565,// Change this to the port you want.
    username: 'Koneko',
    version: '1.20.4'
}
const bot = mineflayer.createBot(options)
bot.on('entityHurt', async (entity) => {
    console.log(entity)
})
