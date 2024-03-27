import * as assert from "assert";

const playerAngryDict: { [key: string]: number } = {};

// 激怒函数
export function rile(username: string) {
    if (!playerAngryDict[username]) {
        playerAngryDict[username] = 0
    }
    playerAngryDict[username] = playerAngryDict[username] + 100
}

// 息怒函数
function propitiate(username: string) {
    assert(playerAngryDict[username], '玩家不在列表中')
    playerAngryDict[username] = playerAngryDict[username] - 1
}

// 每物理时刻调用此函数
export function tickPropitiate() {
    for (const key in playerAngryDict) {
        propitiate(key)
    }
}