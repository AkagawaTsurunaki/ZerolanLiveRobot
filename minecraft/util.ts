import {Bot} from "mineflayer";
import {Vec3} from "vec3";
import {goals, Movements} from "mineflayer-pathfinder";


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
 * 等待指定毫秒数
 * @param ms
 */
export function wait(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

