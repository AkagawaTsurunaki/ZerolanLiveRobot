import {Bot} from "mineflayer";
import {Vec3} from "vec3";
import {goals, Movements} from "mineflayer-pathfinder";


export function moveToPos(bot: Bot, pos: Vec3): void {
    bot.pathfinder.setMovements(new Movements(bot));
    bot.pathfinder.setGoal(new goals.GoalBlock(pos.x, pos.y, pos.z));
}



