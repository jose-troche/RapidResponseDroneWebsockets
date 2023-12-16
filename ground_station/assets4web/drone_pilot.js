const websocket = new WebSocket("ws://localhost:5678/");

const VIDEO_FRAME = 'VIDEO_FRAME';
const RECOGNIZED_OBJECTS = 'RECOGNIZED_OBJECTS';
const SEARCHED_OBJECTS = 'SEARCHED_OBJECTS';
const FIRE_LASER = 'FIRE_LASER';
const VOICE_COMMAND = 'VOICE_COMMAND';
const DRONE_TELEMETRY = 'DRONE_TELEMETRY';
const DRONE_COMMAND = 'DRONE_COMMAND';
const DRONE_BATTERY = 'DRONE_BATTERY';
const DRONE_HEIGHT = 'DRONE_HEIGHT';

const getById = (id) => document.getElementById(id);

// Websocket message handler
websocket.onmessage = ({ data }) => {
    const event = JSON.parse(data);

    if (VIDEO_FRAME in event) {
        getById(VIDEO_FRAME).src = event[VIDEO_FRAME];
    }

    if (RECOGNIZED_OBJECTS in event) {
        const recognized_objects =
            event[RECOGNIZED_OBJECTS].map(i=>`${i.Name} (${i.Confidence.toFixed(1)}%)`).join('<li>');
        getById(RECOGNIZED_OBJECTS).innerHTML = `<li>${recognized_objects}`;
    }

    if (SEARCHED_OBJECTS in event) {
        const searched_objects = event[SEARCHED_OBJECTS].join('<li>');
        getById(SEARCHED_OBJECTS).innerHTML = `<li>${searched_objects}`;
    }

    if (FIRE_LASER in event) {
        const fire_laser_el = getById(FIRE_LASER);
        fire_laser_el.style.display = event[FIRE_LASER] ? 'inline' : 'none';
        setInterval(() => {
            fire_laser_el.style.display = 'none';
        }, 1000);
    }

    if (VOICE_COMMAND in event) {
        getById(VOICE_COMMAND).innerHTML = event[VOICE_COMMAND];
    }

    if (DRONE_TELEMETRY in event) {
        const t = event[DRONE_TELEMETRY];
        getById(DRONE_HEIGHT).innerHTML = t['h'];
        const batteryEl = getById(DRONE_BATTERY);
        batteryEl.innerHTML = `${t['bat']}%`;
        batteryEl.style.backgroundColor = t['bat'] > 60 ? '' : (t['bat'] < 30 ? '#faa' : 'yellow');
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
            const MAX = 60, DECIMALS = 2;
            const a = (controller.axes[0]*MAX).toFixed(DECIMALS);
            const b = (-controller.axes[1]*MAX).toFixed(DECIMALS);
            const d = (controller.axes[2]*MAX).toFixed(DECIMALS);
            const c = (-controller.axes[3]*MAX).toFixed(DECIMALS);
            command = `rc ${a} ${b} ${c} ${d}`;
        }

        wsSend({DRONE_COMMAND: command});

        if (command != 'rc 0.00 0.00 0.00 0.00') {
            getById(DRONE_COMMAND).innerText = command;
        }
    }
}
setInterval(sendDroneCommandFromGamepadState, 100);

function wsSend(payload) {
    websocket.send(JSON.stringify(payload));
}

window.onkeydown = (event) => {
    if (event.key === "Enter") {
        event.preventDefault(); // Cancel the default action, if needed
        setSearchedObjects();
    }
}

// -------------------------------- Set Searched Objects ------------------------------------
function setSearchedObjects() {
    const searched_objects_input = getById('SEARCHED_OBJECTS_INPUT').value;
    if (searched_objects_input) {
        const as_list = searched_objects_input.split(",").map(i => i.trim());
        wsSend({SEARCHED_OBJECTS: as_list});
    }
};
