import {Bot} from "mineflayer";
import {GameEvent, postGameEvent} from "./util";
import {rile} from "./brain/angry"


export async function botHurt(bot: Bot, entityId, sourceTypeId, sourceCauseId, sourceDirectId) {
    // console.log(`${entityId} ${sourceTypeId} ${sourceCauseId} ${sourceDirectId}`)

    if (entityId === bot.entity.id) {
        // console.log(bot.entities)
        const sourceCauseEntity = bot.entities[sourceCauseId - 1]

        if (sourceCauseEntity) {
            // 如果攻击方是玩家, 则会增加愤怒值
            if (sourceCauseEntity.type === 'player') {
                const playerName = sourceCauseEntity.username
                rile(playerName)
                bot.chat(playerName)
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
}
