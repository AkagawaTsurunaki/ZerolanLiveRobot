const mineflayer = require('mineflayer')
const autoeat = require('mineflayer-auto-eat')
const options = {
    host: 'localhost', // Change this to the ip you want.
    port: 25565,// Change this to the port you want.
    username: 'Koneko',
    version: '1.20.4'
}
const bot = mineflayer.createBot(options)

// Load the plugin
bot.loadPlugin(autoeat.plugin)

bot.once('spawn', () => {
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

bot.on('autoeat_stopped', () => {
  console.log('Auto Eat stopped!')
})

bot.on('health', () => {
  if (bot.food === 20) bot.autoEat.disable()
  // Disable the plugin if the bot is at 20 food points
  else bot.autoEat.enable() // Else enable the plugin again
})