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
exports.harvest = exports.fertilize = exports.sow = void 0;
var util_1 = require("./util");
var vec3_1 = require("vec3");
var event_1 = require("./event");
function tryFindBlockToHarvest(bot, maxDistance) {
    if (!bot || !bot.findBlock || typeof bot.findBlock !== 'function') {
        return null;
    }
    return bot.findBlock({
        point: bot.entity.position,
        maxDistance: maxDistance,
        matching: function (block) {
            return block && block.type === bot.registry.blocksByName.wheat.id && block.metadata === 7;
        }
    });
}
function tryFindBlockToSow(bot, maxDistance) {
    if (!bot || !bot.findBlock || typeof bot.findBlock !== 'function') {
        return null;
    }
    return bot.findBlock({
        point: bot.entity.position,
        matching: bot.registry.blocksByName.farmland.id,
        maxDistance: maxDistance,
        useExtraInfo: function (block) {
            var blockAbove = bot.blockAt(block.position.offset(0, 1, 0));
            return !blockAbove || blockAbove.type === 0;
        }
    });
}
function tryFindBlockToFertilize(bot, maxDistance) {
    if (!bot || !bot.findBlock || typeof bot.findBlock !== 'function') {
        return null;
    }
    return bot.findBlock({
        point: bot.entity.position,
        maxDistance: maxDistance,
        matching: function (block) {
            return block && block.type === bot.registry.blocksByName.wheat.id && block.metadata < 7;
        }
    });
}
function sow(bot, maxDistance, interval_ms) {
    if (maxDistance === void 0) { maxDistance = 36; }
    if (interval_ms === void 0) { interval_ms = 100; }
    return __awaiter(this, void 0, void 0, function () {
        var blockToSow, e_1;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, (0, event_1.emitFarmingEvent)(bot)
                    // 找到可以种的地
                ];
                case 1:
                    _a.sent();
                    _a.label = 2;
                case 2:
                    if (!true) return [3 /*break*/, 11];
                    _a.label = 3;
                case 3:
                    _a.trys.push([3, 9, , 10]);
                    blockToSow = tryFindBlockToSow(bot, maxDistance);
                    if (!blockToSow) return [3 /*break*/, 7];
                    (0, util_1.moveToPos)(bot, blockToSow.position.offset(0, 1, 0));
                    // 种地
                    return [4 /*yield*/, bot.equip(bot.registry.itemsByName.wheat_seeds.id, 'hand')];
                case 4:
                    // 种地
                    _a.sent();
                    return [4 /*yield*/, bot.placeBlock(blockToSow, new vec3_1.Vec3(0, 1, 0))
                        // 太快会对服务器造成负担
                    ];
                case 5:
                    _a.sent();
                    // 太快会对服务器造成负担
                    return [4 /*yield*/, (0, util_1.wait)(interval_ms)];
                case 6:
                    // 太快会对服务器造成负担
                    _a.sent();
                    return [3 /*break*/, 8];
                case 7: return [3 /*break*/, 11];
                case 8: return [3 /*break*/, 10];
                case 9:
                    e_1 = _a.sent();
                    console.log(e_1);
                    return [3 /*break*/, 10];
                case 10: return [3 /*break*/, 2];
                case 11: return [4 /*yield*/, (0, event_1.emitFarmedEvent)(bot)];
                case 12:
                    _a.sent();
                    return [2 /*return*/];
            }
        });
    });
}
exports.sow = sow;
function fertilize(bot, maxDistance, interval_ms) {
    if (maxDistance === void 0) { maxDistance = 36; }
    if (interval_ms === void 0) { interval_ms = 100; }
    return __awaiter(this, void 0, void 0, function () {
        var blockToSow, e_2, e_3;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, (0, event_1.emitFertilizingEvent)(bot)
                    // 找到可以种的地
                ];
                case 1:
                    _a.sent();
                    _a.label = 2;
                case 2:
                    if (!true) return [3 /*break*/, 13];
                    _a.label = 3;
                case 3:
                    _a.trys.push([3, 11, , 12]);
                    blockToSow = tryFindBlockToFertilize(bot, maxDistance);
                    if (!blockToSow) return [3 /*break*/, 9];
                    (0, util_1.moveToPos)(bot, blockToSow.position);
                    _a.label = 4;
                case 4:
                    _a.trys.push([4, 6, , 7]);
                    return [4 /*yield*/, bot.equip(bot.registry.itemsByName.bone_meal.id, 'hand')];
                case 5:
                    _a.sent();
                    return [3 /*break*/, 7];
                case 6:
                    e_2 = _a.sent();
                    return [3 /*break*/, 7];
                case 7:
                    bot.placeBlock(blockToSow, new vec3_1.Vec3(0, 1, 0)).catch(function () {
                    });
                    // 太快会对服务器造成负担
                    return [4 /*yield*/, (0, util_1.wait)(interval_ms)];
                case 8:
                    // 太快会对服务器造成负担
                    _a.sent();
                    return [3 /*break*/, 10];
                case 9:
                    bot.stopDigging();
                    return [3 /*break*/, 13];
                case 10: return [3 /*break*/, 12];
                case 11:
                    e_3 = _a.sent();
                    console.log(e_3);
                    return [3 /*break*/, 12];
                case 12: return [3 /*break*/, 2];
                case 13: return [4 /*yield*/, (0, event_1.emitFertilizedEvent)(bot)];
                case 14:
                    _a.sent();
                    return [2 /*return*/];
            }
        });
    });
}
exports.fertilize = fertilize;
function harvest(bot, maxDistance, interval_ms) {
    if (maxDistance === void 0) { maxDistance = 36; }
    if (interval_ms === void 0) { interval_ms = 50; }
    return __awaiter(this, void 0, void 0, function () {
        var blockToSow, e_4;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, (0, event_1.emitHarvestingEvent)(bot)
                    // 找到可以收割的地
                ];
                case 1:
                    _a.sent();
                    _a.label = 2;
                case 2:
                    if (!true) return [3 /*break*/, 10];
                    _a.label = 3;
                case 3:
                    _a.trys.push([3, 8, , 9]);
                    blockToSow = tryFindBlockToHarvest(bot, maxDistance);
                    if (!blockToSow) return [3 /*break*/, 6];
                    (0, util_1.moveToPos)(bot, blockToSow.position);
                    // 收割
                    return [4 /*yield*/, bot.dig(blockToSow)
                        // 太快会对服务器造成负担
                    ];
                case 4:
                    // 收割
                    _a.sent();
                    // 太快会对服务器造成负担
                    return [4 /*yield*/, (0, util_1.wait)(interval_ms)];
                case 5:
                    // 太快会对服务器造成负担
                    _a.sent();
                    return [3 /*break*/, 7];
                case 6:
                    bot.stopDigging();
                    return [3 /*break*/, 10];
                case 7: return [3 /*break*/, 9];
                case 8:
                    e_4 = _a.sent();
                    console.log(e_4);
                    return [3 /*break*/, 9];
                case 9: return [3 /*break*/, 2];
                case 10: return [4 /*yield*/, (0, event_1.emitHarvestedEvent)(bot)];
                case 11:
                    _a.sent();
                    return [2 /*return*/];
            }
        });
    });
}
exports.harvest = harvest;
