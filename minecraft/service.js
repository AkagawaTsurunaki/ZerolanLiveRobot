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
var mineflayer_pathfinder_1 = require("mineflayer-pathfinder");
var mineflayer_1 = require("mineflayer");
var mineflayer_auto_eat_1 = require("mineflayer-auto-eat");
require("mineflayer");
var farm_1 = require("./skill/farm");
var mineflayer_pvp_1 = require("mineflayer-pvp");
var util_1 = require("./util");
var attack_1 = require("./skill/attack");
var follow_1 = require("./skill/follow");
var body_1 = require("./body");
var angry_1 = require("./brain/angry");
var event_1 = require("./event");
var options = {
    host: process.argv[2],
    port: parseInt(process.argv[3]),
    username: process.argv[4],
    password: process.argv[5]
};
var bot = (0, mineflayer_1.createBot)(options);
console.log("\u73A9\u5BB6 ".concat(options.username, " \u6210\u529F\u767B\u5F55 ").concat(options.host, ":").concat(options.port));
bot.loadPlugin(mineflayer_pathfinder_1.pathfinder);
bot.loadPlugin(mineflayer_pvp_1.plugin);
bot.loadPlugin(mineflayer_auto_eat_1.plugin);
bot.once('spawn', function () { return __awaiter(void 0, void 0, void 0, function () {
    return __generator(this, function (_a) {
        // @ts-ignore
        bot.autoEat.options = {
            priority: 'foodPoints',
            startAt: 14,
            bannedFood: []
        };
        return [2 /*return*/];
    });
}); });
bot.on('respawn', function () { return __awaiter(void 0, void 0, void 0, function () {
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0: return [4 /*yield*/, (0, event_1.emitRespawnEvent)(bot)];
            case 1:
                _a.sent();
                return [2 /*return*/];
        }
    });
}); });
bot.on('autoeat_started', function () {
    console.log('Auto Eat started!');
});
bot.on('autoeat_finished', function () {
    console.log('Auto Eat stopped!');
});
bot.on('health', function () {
    if (bot.food === 20)
        bot.autoEat.disable();
    // Disable the plugin if the bot is at 20 food points
    else
        bot.autoEat.enable(); // Else enable the plugin again
});
bot._client.on('damage_event', function (packet) { return __awaiter(void 0, void 0, void 0, function () {
    var entityId, sourceTypeId, sourceCauseId, sourceDirectId;
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                entityId = packet.entityId;
                sourceTypeId = packet.sourceTypeId;
                sourceCauseId = packet.sourceCauseId;
                sourceDirectId = packet.sourceDirectId;
                return [4 /*yield*/, (0, body_1.botHurt)(bot, entityId, sourceTypeId, sourceCauseId, sourceDirectId)];
            case 1:
                _a.sent();
                return [2 /*return*/];
        }
    });
}); });
// @ts-ignore
bot.on("stoppedAttacking", function () {
    var nearestPlayer = (0, util_1.findNearestPlayer)(bot, 5, 50);
    if (nearestPlayer) {
        (0, util_1.moveToPos)(bot, nearestPlayer.position);
    }
});
var fun = 0;
bot.on('physicsTick', function () { return __awaiter(void 0, void 0, void 0, function () {
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0: return [4 /*yield*/, (0, attack_1.attackMobs)(bot)];
            case 1:
                _a.sent();
                fun++;
                if (fun % 20 == 0) {
                    (0, follow_1.followMe)(bot);
                }
                return [4 /*yield*/, (0, angry_1.tickCheckAngry)(bot)];
            case 2:
                _a.sent();
                return [2 /*return*/];
        }
    });
}); });
bot.on('chat', function (username, message, translate, jsonMsg, matches) { return __awaiter(void 0, void 0, void 0, function () {
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                if (!['来', 'lai', 'come'].includes(message)) return [3 /*break*/, 1];
                (0, follow_1.followMe)(bot);
                return [3 /*break*/, 9];
            case 1:
                if (!['种', 'zhong', 'sow'].includes(message)) return [3 /*break*/, 3];
                return [4 /*yield*/, (0, farm_1.sow)(bot)];
            case 2:
                _a.sent();
                return [3 /*break*/, 9];
            case 3:
                if (!['收', 'shou', 'harvest'].includes(message)) return [3 /*break*/, 5];
                return [4 /*yield*/, (0, farm_1.harvest)(bot)];
            case 4:
                _a.sent();
                return [3 /*break*/, 9];
            case 5:
                if (!['施肥', 'shifei', 'fertilize'].includes(message)) return [3 /*break*/, 7];
                return [4 /*yield*/, (0, farm_1.fertilize)(bot)];
            case 6:
                _a.sent();
                return [3 /*break*/, 9];
            case 7:
                if (!['玩', 'wan', 'play'].includes(message)) return [3 /*break*/, 9];
                return [4 /*yield*/, (0, follow_1.wander)(bot)];
            case 8:
                _a.sent();
                _a.label = 9;
            case 9: return [2 /*return*/];
        }
    });
}); });
bot.on('hardcodedSoundEffectHeard', function (soundId, soundCategory, position, volume, pitch) { return __awaiter(void 0, void 0, void 0, function () {
    return __generator(this, function (_a) {
        switch (_a.label) {
            case 0: return [4 /*yield*/, (0, follow_1.faceMe)(bot, position, soundCategory)];
            case 1:
                _a.sent();
                return [2 /*return*/];
        }
    });
}); });
// @ts-ignore
bot.on('attackedTarget', function () {
    (0, angry_1.propitiate)(30);
});
