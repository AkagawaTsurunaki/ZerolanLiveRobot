import {Bot} from "mineflayer";
import {Vec3} from "vec3";
import {goals, Movements} from "mineflayer-pathfinder";
import axios from 'axios';

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
        const playerFilter = e => e.type === 'player'
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

export class GameEvent {
    public read: boolean;
    public time_stamp: number
    public health: number
    public food: number
    public environment: string

    public constructor(bot: Bot, environment: string) {
        this.health = bot.health
        this.food = bot.food
        this.read = false
        this.time_stamp = Date.now()
        this.environment = environment
    }
}

const URL = 'http://127.0.0.1:12546/addevent'

export async function postGameEvent(gameEvent: GameEvent) {
    try {
        const response = await axios.post(URL, gameEvent)
        if (response.status == 200) {
            console.log('成功发送游戏事件')
        }
    } catch (e) {
        console.error(e)
    }
}

export async function addRespawnEvent(bot: Bot) {
    if (bot) {
        const event = new GameEvent(bot, '你重生了。')
        event.health = 20
        event.food = 20
        await postGameEvent(event)
    }
}