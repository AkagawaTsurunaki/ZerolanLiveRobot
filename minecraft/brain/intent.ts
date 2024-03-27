// 高优先级事件

class Intent {
    flag: boolean

    constructor() {
        this.flag = false
    }

    public set() {
        this.flag = true
    }

    public clear() {
        this.flag = false
    }

    public isSet() {
        return this.flag
    }

}

export const fightingWithHostiles = new Intent()