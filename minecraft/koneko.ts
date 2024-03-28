import {Bot} from "mineflayer";

/**
 * The main Koneko Bot plugin class.
 */
export class Koneko {
    private readonly bot: Bot;


    private avgEnvLight() {
        const blocks = findBlocksNearAirBlock(bot, 256, 1024)
        if (blocks) {
            const blockCount = blocks.length
            const lightArr = blocks.map(block => block.skyLight)
            const lightSum = lightArr.reduce((total, num) => total + num, 0);
            return lightSum / blockCount
        }
    }
}