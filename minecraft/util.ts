import {Bot} from "mineflayer";
import {Vec3} from "vec3";
import {goals, Movements} from "mineflayer-pathfinder";
import {Block} from 'prismarine-block'

export function moveToPos(bot: Bot, pos: Vec3): void {
    bot.pathfinder.setMovements(new Movements(bot));
    bot.pathfinder.setGoal(new goals.GoalBlock(pos.x, pos.y, pos.z));
}


/**
 * 寻找最近的玩家
 * @param bot Bot 对象
 * @param min_dist 最小搜索半径
 * @param max_dist 最大搜索半径
 * @returns {Entity|null}
 */
export function findNearestPlayer(bot: Bot, min_dist = 0, max_dist = 255) {
    const player_filter = e => e.type === 'player'
    const player = bot.nearestEntity(player_filter)
    if (player) {
        const dist = player.position.distanceTo(bot.entity.position)
        if (min_dist < dist && dist < max_dist) {
            return player
        }
    }
    return null
}

/**
 * 按照玩家名称查找玩家实体。如果找不到，则返回 null。
 * @param bot
 * @param username
 */
export function findPlayerByUsername(bot: Bot, username: string) {
    if (bot && username) {
        for (const id in bot.entities) {
            const e = bot.entities[id]
            if (e.username && e.username === username) {
                return e
            }
        }
    }
    return null
}

/**
 * 等待指定毫秒数
 * @param ms
 */
export function wait(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * 目标方块附近是否毗邻指定方块名。例如，targetBlock 周围是否挨着名称为 air 的方块，若果存在返回 true 否则返回 false。
 * @param bot Bot 对象
 * @param targetBlock 目标方块
 * @param neighborBlockName 毗邻的方块名
 */
function neighbor(bot: Bot, targetBlock: Block, neighborBlockName: string) {

    return bot.blockAt(targetBlock.position.offset(1, 0, 0), false).name === neighborBlockName ||
        bot.blockAt(targetBlock.position.offset(-1, 0, 0), false).name === neighborBlockName ||
        bot.blockAt(targetBlock.position.offset(0, 1, 0), false).name === neighborBlockName ||
        bot.blockAt(targetBlock.position.offset(0, -1, 0), false).name === neighborBlockName ||
        bot.blockAt(targetBlock.position.offset(0, 0, 1), false).name === neighborBlockName ||
        bot.blockAt(targetBlock.position.offset(0, 0, -1), false).name === neighborBlockName;

}


/**
 * 查找附近半径范围内的所有被空气覆盖的方块
 */
function findBlocksNearAirBlock(bot: Bot, maxDistance: number, count: number) {
    if (bot) {
        const useExtraInfo = false
        const blockPosList = bot.findBlocks({
            point: bot.entity.position,
            matching: (block) => {
                return neighbor(bot, block, 'air')
            },
            maxDistance: maxDistance,
            count: count,
            useExtraInfo: useExtraInfo
        })
        return blockPosList.map(blockPos => bot.blockAt(blockPos))
    }
    return null
}


