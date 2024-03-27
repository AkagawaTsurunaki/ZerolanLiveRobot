const lovePlayerDict: { [key: string]: number } = {};

class RobotEvent {
    private name: string
    private love?: number
    private angry?: number

    constructor(name: string, love: number, angry: number) {
        this.name = name
        this.angry = angry
        this.love = love
    }
}

export async function addLove(event: RobotEvent) {

}