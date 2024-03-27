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
                rile(playerName)
            }
            await emitBotHurtEvent(bot, sourceCauseEntity)
        }
    }
}
