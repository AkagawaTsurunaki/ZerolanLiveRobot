// 高优先级事件

class Intent {
    flag: boolean
    value: number

    constructor(value: number) {
        this.flag = false
        this.value = value
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

export const fightingWithHostiles = new Intent(100)