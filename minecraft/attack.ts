import {Bot} from "mineflayer";
import "mineflayer-pvp/lib/index";

export async function attackMobs(bot: Bot) {
    const mobFilter = e => (e.type === 'hostile' || e.displayName == 'Phantom') && e.position.distanceTo(bot.entity.position) < 8
    const entity = bot.nearestEntity(mobFilter)
    if (entity) {
        await bot.pvp.attack(entity)
    }
}

