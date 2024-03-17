import {Bot} from "mineflayer";
import {moveToPos} from "./util";
import {Vec3} from "vec3";

function tryFindBlockToHarvest(bot: Bot, maxDistance: number) {
    if (!bot || !bot.findBlock || typeof bot.findBlock !== 'function') {
        return null;
    }
    return bot.findBlock({
        point: bot.entity.position,
        maxDistance: maxDistance,
        matching: (block) => {
            return block && block.type === bot.registry.blocksByName.wheat.id && block.metadata === 7
        }
    })
}


function tryFindBlockToSow(bot: Bot, maxDistance: number) {
    if (!bot || !bot.findBlock || typeof bot.findBlock !== 'function') {
        return null;
    }
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


export async function sow(bot: Bot, maxDistance = 16) {
    try {
        // 找到可以种的地
        while (tryFindBlockToSow(bot, maxDistance)) {
            const blockToSow = tryFindBlockToSow(bot, maxDistance)
            console.log(blockToSow.metadata)
            if (blockToSow) {
                bot.chat('锄大地喵~')
                moveToPos(bot, blockToSow.position.offset(0, 1, 0))
                // 种地
                await bot.equip(bot.registry.itemsByName.wheat_seeds.id, 'hand')
                await bot.placeBlock(blockToSow, new Vec3(0, 1, 0))
            }
            setTimeout(sow, 1000)
        }
    } catch (e) {
        console.log(e)
    }
}

