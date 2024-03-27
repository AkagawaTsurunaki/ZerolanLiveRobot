import {Bot} from "mineflayer";
import {findPlayerByUsername} from "../util";
import {emitPropitiateEvent, emitRileEvent} from "../event";

const playerAngryDict: { [key: string]: number } = {};
const mercyAngryValueThreshold: number = 100
const attackAngryValueThreshold: number = 200
const rileValue: number = 100

// 激怒函数
export function rile(username: string) {
    if (!playerAngryDict[username]) {
        playerAngryDict[username] = 0
    }
    playerAngryDict[username] = playerAngryDict[username] + rileValue
}

// 息怒函数
export function propitiate(propitiateValue: number) {
    propitiateValue = Math.abs(propitiateValue)
    for (const username in playerAngryDict) {
        playerAngryDict[username] = playerAngryDict[username] - propitiateValue
        if (playerAngryDict[username] < 0) {
            playerAngryDict[username] = 0
        }
    }
}


/**
 * 当正在被攻击的玩家生命值低于 mercyHealthThreshold 时，尝试饶恕玩家。
 * @param bot
 */
async function tryMercy(bot: Bot) {
    const pvpTarget = bot.pvp.target

    if (pvpTarget) {
        const username = pvpTarget.username
        const player = pvpTarget
        if (player && player.type == 'player') {
            // 愤怒值过低时饶恕玩家
            if (playerAngryDict[username] < mercyAngryValueThreshold) {
                emitPropitiateEvent(bot, username).then(() => {
                    bot.pvp.stop()
                })
            }
        }
    }
}

/**
 * 查找具有最大的激怒值的且超过阈值 attackAngryValueThreshold 的玩家
 * @param bot
 */
async function tryAttackPlayer(bot: Bot) {
    let maxValue = 0
    let username: string
    for (const key in playerAngryDict) {
        if (maxValue < playerAngryDict[key]) {
            maxValue = playerAngryDict[key]
            username = key
        }
    }
    const maxAngryValuePlayer = findPlayerByUsername(bot, username)
    if (maxValue > attackAngryValueThreshold) {
        emitRileEvent(bot, username).then(() => {
            bot.pvp.attack(maxAngryValuePlayer)
        })
    }
}

// 每物理时刻调用此函数
export async function tickCheckAngry(bot: Bot) {
    tryAttackPlayer(bot)
    tryMercy(bot)
    propitiate(1)
    bot.chat(`${playerAngryDict['Akagawa']}`)
}