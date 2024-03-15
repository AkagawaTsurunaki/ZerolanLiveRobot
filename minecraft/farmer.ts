import {Bot} from "mineflayer";
import {moveToPos} from "./util";

function findBlockToHarvest(bot: Bot, maxDistance = 6) {
    return bot.findBlock({
        point: bot.entity.position,
        maxDistance: maxDistance,
        matching: (block) => {
            return block && block.type === bot.registry.blocksByName.wheat.id && block.metadata === 7
        }
    })
}


function findBlockToSow(bot: Bot, maxDistance = 16) {
    return bot.findBlock({
        point: bot.entity.position,
        matching: bot.registry.blocksByName.farmland.id,
        maxDistance: maxDistance,
        useExtraInfo: (block) => {
            const blockAbove = bot.blockAt(block.position.offset(0, 1, 0))
            return !blockAbove || blockAbove.type === 0
        }
    })
}


export function sow(bot: Bot) {
    const blockToSow = findBlockToSow(bot, 16)
    if (blockToSow) {
        bot.chat('开始')
        moveToPos(bot, blockToSow.position)
    }
}