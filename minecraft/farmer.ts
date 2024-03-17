import {Bot} from "mineflayer";
import {moveToPos, wait} from "./util";
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


export async function sow(bot: Bot, maxDistance = 16, interval_ms = 500) {
    try {
        bot.chat('开始锄大地喵~')

        // 找到可以种的地
        while (tryFindBlockToSow(bot, maxDistance)) {
            const blockToSow = tryFindBlockToSow(bot, maxDistance)
            console.log(blockToSow.metadata)
            if (blockToSow) {

                moveToPos(bot, blockToSow.position.offset(0, 1, 0))
                // 种地
                await bot.equip(bot.registry.itemsByName.wheat_seeds.id, 'hand')
                await bot.placeBlock(blockToSow, new Vec3(0, 1, 0))
                // 太快会对服务器造成负担
                await wait(interval_ms)
            }
        }
        bot.chat('已经把所有的小种子播撒到里面了哦~')
    } catch (e) {
        console.log(e)
    }
}

export async function fertilize(bot: Bot,) {
    try {

    } catch (e) {
        console.log(e)
    }
}