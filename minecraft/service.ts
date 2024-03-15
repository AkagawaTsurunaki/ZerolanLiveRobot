import {pathfinder} from "mineflayer-pathfinder";
import {createBot} from "mineflayer";
import "mineflayer"
import {sow} from "./farmer"


const bot = createBot({
    host: 'localhost',
    port: 25565,
    username: 'Koneko'
})

bot.loadPlugin(pathfinder)

bot.on("chat", (username, message, translate, jsonMsg) => {
    if (message === '种') {
        sow(bot)
    }
})