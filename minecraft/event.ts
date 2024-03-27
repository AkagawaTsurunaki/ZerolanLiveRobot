import {Bot} from "mineflayer";
import axios from "axios";
import {Entity} from "prismarine-entity"

const URL = 'http://127.0.0.1:12546/addevent'

// 待发送的游戏事件
const gameEvents: GameEvent[] = []

enum EventType {
    RILE_EVENT,
    PROPITIATE,
    RESPAWN,
    FARMING,
    FARMED,
    FERTILIZING,
    FERTILIZED,
    HARVESTING,
    HARVESTED,
    BOT_HURT,
}

export class GameEvent {
    public read: boolean;
    public time_stamp: number
    public health: number
    public food: number
    public environment: string
    public event_type: EventType

    public constructor(bot: Bot, eventType: EventType, environment: string) {
        this.health = bot.health
        this.food = bot.food
        this.read = false
        this.event_type = eventType
        this.time_stamp = Date.now()
        this.environment = environment
    }
}

export async function postGameEvent(gameEvent: GameEvent) {
    try {
        const response = await axios.post(URL, gameEvent)
        if (response.status == 200) {
            console.debug('成功发送游戏事件')
            console.log(gameEvent.environment)
        }
    } catch (e) {
    }
}

export async function emitRileEvent(bot: Bot, playerName: string) {
    if (bot && playerName) {
        const env: string = `你被彻底激怒了, 因为 ${playerName} 总是在攻击你, 你很生气!!! 现在你正在使出全力还击!`
        const gameEvent = new GameEvent(bot, EventType.RILE_EVENT, env)
        await postGameEvent(gameEvent)
    }
}

export async function emitRespawnEvent(bot: Bot) {
    if (bot) {
        const env: string = '你在游戏中死亡后又重生了。'
        const event = new GameEvent(bot, EventType.RESPAWN, env)
        event.health = 20
        event.food = 20
        await postGameEvent(event)
    }
}

export async function emitPropitiateEvent(bot: Bot, playerName: string) {
    if (bot) {
        const env: string = `你平息了对 ${playerName} 的怒火, 决定停止还击`
        const event = new GameEvent(bot, EventType.PROPITIATE, env)
        await postGameEvent(event)
    }
}

export async function emitFarmingEvent(bot: Bot) {
    if (bot) {
        const env: string = '你开始了耕作, 很开心'
        const event = new GameEvent(bot, EventType.FARMING, env)
        await postGameEvent(event)
    }
}

export async function emitFarmedEvent(bot: Bot) {
    if (bot) {
        const env: string = '你已经把所有的种子播撒到耕地中了, 很开心.'
        const event = new GameEvent(bot, EventType.FARMED, env)
        await postGameEvent(event)
    }
}

export async function emitFertilizingEvent(bot: Bot) {
    if (bot) {
        const env: string = '你开始向耕地施肥'
        const event = new GameEvent(bot, EventType.FERTILIZING, env)
        await postGameEvent(event)
    }
}

export async function emitFertilizedEvent(bot: Bot) {
    if (bot) {
        const env: string = '你对耕地的施肥已经完毕'
        const event = new GameEvent(bot, EventType.FERTILIZED, env)
        await postGameEvent(event)
    }
}

export async function emitHarvestingEvent(bot: Bot) {
    if (bot) {
        const env: string = '你开始收割作物... 真开心!'
        const event = new GameEvent(bot, EventType.HARVESTING, env)
        await postGameEvent(event)
    }
}

export async function emitHarvestedEvent(bot: Bot) {
    if (bot) {
        const env: string = '你完成了收割作物! 真开心!'
        const event = new GameEvent(bot, EventType.HARVESTED, env)
        await postGameEvent(event)
    }
}

export async function emitBotHurtEvent(bot: Bot, srcEntity: Entity) {
    if (bot) {
        let scrName: string
        if (srcEntity.displayName) {
            scrName = srcEntity.displayName
        } else {
            scrName = srcEntity.type
        }
        const env: string = `你受伤了, 来源是 ${scrName}`
        const event = new GameEvent(bot, EventType.BOT_HURT, env)
        await postGameEvent(event)
    }
}