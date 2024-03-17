import {moveToPos} from "./util";
import {Bot} from "mineflayer";
import {Vec3} from "vec3";
import {
    tool_icon_freehand_draw
} from "../../../../ProgramFiles/Anaconda/Lib/site-packages/bokeh/server/static/js/lib/styles/icons.css";

export function followMe(bot: Bot) {
    const player_filter = e => e.type === 'player' && e.position.distanceTo(bot.entity.position) > 5
    const player_entity = bot.nearestEntity(player_filter)
    if (player_entity) {
        // bot.chat('好的喵, 主人!')
        moveToPos(bot, player_entity.position)
        bot.lookAt(player_entity.position.offset(0, 1, 0))
    }
}

export async function faceMe(bot: Bot, position: Vec3, soundCategory) {
    const distance = bot.entity.position.distanceTo(position)
    if (soundCategory === 'player') {
        if (1 < distance && distance < 20) {
            await bot.lookAt(position)
        }
    } else if (soundCategory === 'hostile') {
        if (distance < 20) {
            await bot.lookAt(position)
        }
    }
}