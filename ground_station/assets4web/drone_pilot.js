const websocket = new WebSocket("ws://localhost:5678/");
function getById(id) { return document.getElementById(id); }

window.onkeydown = (event) => {
    if (event.key === "Enter") {
        event.preventDefault(); // Cancel the default action, if needed
        setSearchObjects();
    }
}

// -------------------------------- Set Searched Objects ------------------------------------
function setSearchedObjects(){
    const searched_objects_input = searched_objects_el.value;
    if (searched_objects_input) {
        const list = searched_objects_input.split(",").map(i => i.trim())
        websocket.send(JSON.stringify(list));
    }
};

window.addEventListener("DOMContentLoaded", () => {
    const VIDEO_FRAME = 'VIDEO_FRAME';
    const RECOGNIZED_OBJECTS = 'RECOGNIZED_OBJECTS';
    const SEARCHED_OBJECTS = 'SEARCHED_OBJECTS';
    const FIRE_LASER = 'FIRE_LASER';
    const VOICE_COMMAND = 'VOICE_COMMAND';
    const DRONE_TELEMETRY = 'DRONE_TELEMETRY';
    const DRONE_COMMAND = 'DRONE_COMMAND';

    const   drone_command_el = getById(DRONE_COMMAND),
        drone_telemetry_el = getById(DRONE_TELEMETRY),
        voice_command_el = getById(VOICE_COMMAND),
        fire_laser_el = getById(FIRE_LASER),
        searched_objects_el = getById(SEARCHED_OBJECTS),
        recognized_objects_el = getById(RECOGNIZED_OBJECTS),
        video_frame_el = getById(VIDEO_FRAME);

    // Websocket message handler
    websocket.onmessage = ({ data }) => {
        const event = JSON.parse(data);
        if (VIDEO_FRAME in event) {
            video_frame_el.src = event[VIDEO_FRAME];
        }

        if (RECOGNIZED_OBJECTS in event) {
            const recognized_objects = 
                event[RECOGNIZED_OBJECTS].join('<li>');
            recognized_objects_el.innerHTML = `<li>${recognized_objects}`;
        }

        if (SEARCHED_OBJECTS in event) {
            const searched_objects = 
                event[SEARCHED_OBJECTS].join('<li>');
            searched_objects_el.innerHTML = `<li>${searched_objects}`;
        }

        if (FIRE_LASER in event) {
            fire_laser_el.style.display = event[FIRE_LASER] ? 'inline' : 'none';
        }

        if (VOICE_COMMAND in event) {
            voice_command_el.innerHTML = event[VOICE_COMMAND];
        }

        if (DRONE_TELEMETRY in event) {
            const t = event[DRONE_TELEMETRY];
            drone_telemetry_el.innerHTML = `Battery: ${t['bat']}%<li>Height: ${t['h']||0} cm`;
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

            if (command != 'rc 0.0000 0.0000 0.0000 0.0000') {
                drone_command_el.innerText = command;
            }
        }
    }
    setInterval(sendDroneCommandFromGamepadState, 100);

    function sendDroneCommand(command) {
        websocket.send(JSON.stringify({ DRONE_COMMAND: command }));
    }
});
