import {Bot} from "mineflayer";
import {rile} from "./brain/angry"
import {emitBotHurtEvent} from "./event";


export async function botHurt(bot: Bot, entityId, sourceTypeId, sourceCauseId, sourceDirectId) {
    if (entityId === bot.entity.id) {
        const sourceCauseEntity = bot.entities[sourceCauseId - 1]

        if (sourceCauseEntity) {
            // 如果攻击方是玩家, 则会增加愤怒值
            if (sourceCauseEntity.type === 'player') {
                const playerName = sourceCauseEntity.username
                rile(bot, playerName)
            }
            await emitBotHurtEvent(bot, sourceCauseEntity)
        }
    }
}

export async function botInterrupt(bot: Bot, entityId, sourceTypeId, sourceCauseId, sourceDirectId) {
    if (entityId === bot.entity.id) {
        const sourceCauseEntity = bot.entities[sourceCauseId - 1]

        if (sourceCauseEntity) {
            if (sourceCauseEntity.type === 'player') {
                if (!bot.pvp.target) {
                    bot.pathfinder.stop()
                }
            }
        }
    }
}