"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.addRespawnEvent = exports.postGameEvent = exports.GameEvent = exports.wait = exports.findPlayerByUsername = exports.findNearestPlayer = exports.moveToPos = void 0;
var mineflayer_pathfinder_1 = require("mineflayer-pathfinder");
var axios_1 = require("axios");
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
        var playerFilter = function (e) { return e.type === 'player'; };
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
var GameEvent = /** @class */ (function () {
    function GameEvent(bot, environment) {
        this.health = bot.health;
        this.food = bot.food;
        this.read = false;
        this.time_stamp = Date.now();
        this.environment = environment;
    }
    return GameEvent;
}());
exports.GameEvent = GameEvent;
var URL = 'http://127.0.0.1:12546/addevent';
function postGameEvent(gameEvent) {
    return __awaiter(this, void 0, void 0, function () {
        var response, e_1;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    return [4 /*yield*/, axios_1.default.post(URL, gameEvent)];
                case 1:
                    response = _a.sent();
                    if (response.status == 200) {
                        console.log('成功发送游戏事件');
                    }
                    return [3 /*break*/, 3];
                case 2:
                    e_1 = _a.sent();
                    console.error(e_1);
                    return [3 /*break*/, 3];
                case 3: return [2 /*return*/];
            }
        });
    });
}
exports.postGameEvent = postGameEvent;
function addRespawnEvent(bot) {
    return __awaiter(this, void 0, void 0, function () {
        var event_1;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    if (!bot) return [3 /*break*/, 2];
                    event_1 = new GameEvent(bot, '你重生了。');
                    event_1.health = 20;
                    event_1.food = 20;
                    return [4 /*yield*/, postGameEvent(event_1)];
                case 1:
                    _a.sent();
                    _a.label = 2;
                case 2: return [2 /*return*/];
            }
        });
    });
}
exports.addRespawnEvent = addRespawnEvent;
