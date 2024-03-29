import {Bot} from "mineflayer";
import {GameEvent, moveToPos, postGameEvent, wait} from "./util";
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

function tryFindBlockToFertilize(bot: Bot, maxDistance: number) {
    if (!bot || !bot.findBlock || typeof bot.findBlock !== 'function') {
        return null;
    }
    return bot.findBlock({
        point: bot.entity.position,
        maxDistance: maxDistance,
        matching: (block) => {
            return block && block.type === bot.registry.blocksByName.wheat.id && block.metadata < 7
        }
    })
}

export async function sow(bot: Bot, maxDistance = 36, interval_ms = 100) {
    await postGameEvent(new GameEvent(bot, '开始锄大地喵~开心！'))
    // 找到可以种的地
    while (true) {
        try {
            let blockToSow = tryFindBlockToSow(bot, maxDistance);

            if (blockToSow) {

                moveToPos(bot, blockToSow.position.offset(0, 1, 0))
                // 种地
                await bot.equip(bot.registry.itemsByName.wheat_seeds.id, 'hand')
                await bot.placeBlock(blockToSow, new Vec3(0, 1, 0))
                // 太快会对服务器造成负担
                await wait(interval_ms)

            } else {
                break
            }
        } catch (e) {
            console.log(e)
        }
    }
    await postGameEvent(new GameEvent(bot, '已经把所有的小种子播撒到里面了哦~'))
}


export async function fertilize(bot: Bot, maxDistance = 36, interval_ms = 100) {
    await postGameEvent(new GameEvent(bot, '开始施肥了，好爽。'))
    // 找到可以种的地
    while (true) {
        try {
            const blockToSow = tryFindBlockToFertilize(bot, maxDistance)

            if (blockToSow) {

                moveToPos(bot, blockToSow.position)
                // 种地
                try {
                    await bot.equip(bot.registry.itemsByName.bone_meal.id, 'hand')

                } catch (e) {
                    console.log('没有这个工具')
                    bot.chat('没骨粉啊!')
                }
                bot.placeBlock(blockToSow, new Vec3(0, 1, 0)).catch(() => {
                })
                // 太快会对服务器造成负担
                await wait(interval_ms)
            } else {
                bot.stopDigging()
                break
            }
        } catch (e) {
            console.log(e)
        }

    }
    await postGameEvent(new GameEvent(bot, '施肥完毕，真棒！'))
}

export async function harvest(bot: Bot, maxDistance = 36, interval_ms = 50) {
    await postGameEvent(new GameEvent(bot, '开始收割作物了。好开心喵！'))
    // 找到可以收割的地
    while (true) {
        try {
            const blockToSow = tryFindBlockToHarvest(bot, maxDistance)
            if (blockToSow) {
                moveToPos(bot, blockToSow.position)
                // 收割
                await bot.dig(blockToSow)
                // 太快会对服务器造成负担
                await wait(interval_ms)
            } else {
                bot.stopDigging()
                break
            }
        } catch (e) {
            console.log(e)
        }
    }
    await postGameEvent(new GameEvent(bot, '把作物收割好了，真棒！'))
}