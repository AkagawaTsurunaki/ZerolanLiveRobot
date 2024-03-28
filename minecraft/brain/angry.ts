import {Bot} from "mineflayer";
import {findPlayerByUsername} from "../util";
import {emitPropitiateEvent, emitRileEvent} from "../event";
import {p} from "../../../../../ProgramFiles/Anaconda/Lib/site-packages/bokeh/server/static/js/lib/core/dom";
import {np} from "../../../../../ProgramFiles/Anaconda/Lib/site-packages/bokeh/server/static/js/lib/api/linalg";
import pow = np.pow;

// 愤怒表: 记录机器人对每个玩家的愤怒值
const playerAngryDict: { [key: string]: number } = {};

// 机器人的愤怒值降低到多少时会选择宽恕玩家
const mercyAngryValueThreshold: number = 100

// 机器人达到多少愤怒值时会攻击玩家
const attackAngryValueThreshold: number = 200

// 机器人受到玩家攻击时会增加多少愤怒值
const rileValue: number = 60

// 激怒函数
export function rile(bot: Bot, username: string) {
    if (!playerAngryDict[username]) {
        playerAngryDict[username] = 0
    }
    const pvpTarget = bot.pvp.target
    if (pvpTarget && pvpTarget.type === 'player') {
        pvpTarget.username = username
        playerAngryDict[username] += rileValue / 2
        if (bot.health < 20) {
            playerAngryDict[username] += rileValue * (21 - bot.health)
        }
    } else {
        playerAngryDict[username] += rileValue
    }
}

// 息怒函数
export function propitiate(propitiateValue: number = rileValue) {
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
    // console.debug(`${playerAngryDict['Akagawa']}`)
}