"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.wait = exports.findPlayerByUsername = exports.findNearestPlayer = exports.moveToPos = void 0;
var mineflayer_pathfinder_1 = require("mineflayer-pathfinder");
function moveToPos(bot, pos) {
    bot.pathfinder.setMovements(new mineflayer_pathfinder_1.Movements(bot));
    bot.pathfinder.setGoal(new mineflayer_pathfinder_1.goals.GoalBlock(pos.x, pos.y, pos.z));
}
exports.moveToPos = moveToPos;
/**
 * 寻找最近的玩家
 * @param bot Bot 对象
 * @param min_dist 最小搜索半径
 * @param max_dist 最大搜索半径
 * @returns {Entity|null}
 */
function findNearestPlayer(bot, min_dist, max_dist) {
    if (min_dist === void 0) { min_dist = 0; }
    if (max_dist === void 0) { max_dist = 255; }
    var player_filter = function (e) { return e.type === 'player'; };
    var player = bot.nearestEntity(player_filter);
    if (player) {
        var dist = player.position.distanceTo(bot.entity.position);
        if (min_dist < dist && dist < max_dist) {
            return player;
        }
    }
    return null;
}
exports.findNearestPlayer = findNearestPlayer;
/**
 * 按照玩家名称查找玩家实体。如果找不到，则返回 null。
 * @param bot
 * @param username
 */
function findPlayerByUsername(bot, username) {
    if (bot && username) {
        for (var id in bot.entities) {
            var e = bot.entities[id];
            if (e.username && e.username === username) {
                return e;
            }
        }
    }
    return null;
}
exports.findPlayerByUsername = findPlayerByUsername;
/**
 * 等待指定毫秒数
 * @param ms
 */
function wait(ms) {
    return new Promise(function (resolve) { return setTimeout(resolve, ms); });
}
exports.wait = wait;
function calculateMillisecondsDifference(timestamp1, timestamp2) {
    return Math.abs(timestamp1 - timestamp2);
}
