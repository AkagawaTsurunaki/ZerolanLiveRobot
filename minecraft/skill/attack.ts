import {Bot} from "mineflayer";
import "mineflayer-pvp/lib/index";
import {fightingWithHostiles} from "../brain/intent";


export async function attackMobs(bot: Bot) {
    const mobFilter = e => (e.type === 'hostile' || e.displayName == 'Phantom') && e.position.distanceTo(bot.entity.position) < 8
    const entity = bot.nearestEntity(mobFilter)
    if (entity) {
        fightingWithHostiles.set()
        await bot.pvp.attack(entity)
    }
}