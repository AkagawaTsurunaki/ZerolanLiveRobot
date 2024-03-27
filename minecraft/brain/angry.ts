import * as assert from "assert";
import {Bot} from "mineflayer";

const playerAngryDict: { [key: string]: number } = {};
const mercyHealthThreshold: number = 3
const rileValue: number = 100
const propitiateValue: number = 1

// 激怒函数
export function rile(username: string) {
    if (!playerAngryDict[username]) {
        playerAngryDict[username] = 0
    }
    playerAngryDict[username] = playerAngryDict[username] + rileValue
}

// 息怒函数
function propitiate(username: string) {
    assert(playerAngryDict[username], '玩家不在列表中')
    playerAngryDict[username] = playerAngryDict[username] - propitiateValue
    if (playerAngryDict[username] < 0) {
        playerAngryDict[username] = 0
    }
}


/**
 * 当正在被攻击的玩家生命值低于 mercyHealthThreshold 时，尝试饶恕玩家。
 * @param bot
 */
async function tryMercy(bot: Bot) {
    const username = bot.pvp.target.username
    const player = bot.entities[username]
    if (player && player.type == 'player') {
        if (player.health < mercyHealthThreshold) {
            playerAngryDict[username] = 0
            await bot.pvp.stop()
        }
    }
}

// 每物理时刻调用此函数
export async function tickCheckAngry(bot: Bot) {
    for (const key in playerAngryDict) {
        propitiate(key)
    }
    await tryMercy(bot)
}