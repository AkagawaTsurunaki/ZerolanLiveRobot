import {Bot} from "mineflayer";
import {GameEvent, postGameEvent} from "./util";
import {rile} from "./brain"


export async function botHurt(bot: Bot, entityId, sourceTypeId, sourceCauseId, sourceDirectId) {
    if (entityId === bot.entity.id) {
        const sourceCauseEntity = bot.entities[sourceCauseId]

        // 如果攻击方是玩家, 则会增加愤怒值
        if (sourceCauseEntity.type == 'player') {
            const playerName = sourceCauseEntity.username
            rile(playerName)
        }

        let botHurtEvent: GameEvent
        if (sourceCauseEntity.displayName) {
            botHurtEvent = new GameEvent(bot, `你受伤了, 来源是${sourceCauseEntity.displayName}`)
        } else {
            botHurtEvent = new GameEvent(bot, `你受伤了, 来源是${sourceCauseEntity.type}`)
        }

        await postGameEvent(botHurtEvent)
    }
}
