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