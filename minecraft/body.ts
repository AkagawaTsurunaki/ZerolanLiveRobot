import {Bot} from "mineflayer";
import {GameEvent, postGameEvent} from "./util";

export async function botHurt(bot: Bot, entityId) {
    if (entityId === bot.entity.id) {
        const botHurtEvent = new GameEvent(bot, '你受伤了。')
        await postGameEvent(botHurtEvent)
    }
}
