const VIDEO_FRAME = 'VIDEO_FRAME';
const RECOGNIZED_OBJECTS = 'RECOGNIZED_OBJECTS';
const SEARCHED_OBJECTS = 'SEARCHED_OBJECTS';
const FIRE_LASER = 'FIRE_LASER';
const VOICE_COMMAND = 'VOICE_COMMAND';
const DRONE_TELEMETRY = 'DRONE_TELEMETRY';
const DRONE_COMMAND = 'DRONE_COMMAND';

window.addEventListener("DOMContentLoaded", () => {
    const websocket = new WebSocket("ws://localhost:5678/");

    // Websocket message handler
    websocket.onmessage = ({ data }) => {
        const event = JSON.parse(data);
        if (VIDEO_FRAME in event) {
            event[VIDEO_FRAME]
        }

        if (RECOGNIZED_OBJECTS in event) {
            console.log(event[RECOGNIZED_OBJECTS])
        }

        if (SEARCHED_OBJECTS in event) {
            console.log(event[SEARCHED_OBJECTS])
        }

        if (FIRE_LASER in event) {
            console.log(event[FIRE_LASER])
        }

        if (VOICE_COMMAND in event) {
            console.log(event[VOICE_COMMAND])
        }

        if (DRONE_TELEMETRY in event) {
            console.log(event[DRONE_TELEMETRY])
        }
    };

    // ------------------------  Send Drone commands mapped from GamePad ------------------------------
    //   Drone commands conform to:
    //   https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf
    function sendDroneCommandFromGamepadState() {
        const controller = navigator.getGamepads ? navigator.getGamepads()[0] : false;

        if (controller) {
            let command = "";

            if (controller.buttons[3].pressed) command = "takeoff"; // X
            else if (controller.buttons[0].pressed) command = "land"; // B
            else if (controller.buttons[1].pressed) command = "streamon"; // A
            else if (controller.buttons[2].pressed) command = "streamoff"; // Y
            else if (controller.buttons[6].pressed) command = "flip l"; // ZL
            else if (controller.buttons[7].pressed) command = "flip r"; // ZR
            else if (controller.buttons[12].pressed) command = "up 40"; // ^
            else if (controller.buttons[13].pressed) command = "down 40"; // v
            else if (controller.buttons[14].pressed) command = "left 30"; // <-
            else if (controller.buttons[15].pressed) command = "right 30"; // ->
            else { // Just send an rc command wth the axes data
                const MAX = 60, DECIMALS = 4;
                const a = (controller.axes[0]*MAX).toFixed(DECIMALS);
                const b = (-controller.axes[1]*MAX).toFixed(DECIMALS);
                const d = (controller.axes[2]*MAX).toFixed(DECIMALS);
                const c = (-controller.axes[3]*MAX).toFixed(DECIMALS);
                command = `rc ${a} ${b} ${c} ${d}`;
            }

            sendDroneCommand(command);
        }
    }
    setInterval(sendDroneCommandFromGamepadState, 200);

    function sendDroneCommand(DRONE_COMMAND) {
        websocket.send(JSON.stringify({ DRONE_COMMAND }));
    }
});
