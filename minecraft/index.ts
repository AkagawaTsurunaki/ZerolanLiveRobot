import { Bot } from "mineflayer";

import { PVP } from "./koneko";

export function plugin(bot: Bot)
{
    const pvp = new PVP(bot);
    bot.pvp = pvp;
}