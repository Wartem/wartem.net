let canvas = document.querySelector('canvas');
let ctx = canvas.getContext('2d');
let fps = 99;
let activated = true;

let userInputAllowed = true;
let mouseOnCanvasX = canvas.width / 2;
let mouseOnCanvasY = canvas.height / 2;

const allApps = document.querySelectorAll('.nav-item');

let canvasSectionH1 = document.querySelector('#canvas-section-h1');
let canvasSectionH2 = document.querySelector('#canvas-section-h2');

const fpsSlider = document.querySelector('#fps-slider');
fpsSlider.value = fps;

document.getElementById("fps-slider").oninput = function () {
    fps = fpsSlider.value;

    document.querySelector('#fps-text').innerHTML = "Speed: " + fps + "/100";
};

const balls_1 = document.querySelector('#nav-item-1');
const paint_2 = document.querySelector('#nav-item-2');
const navItem_3 = document.querySelector('#nav-item-3');
const navItem_4 = document.querySelector('#nav-item-4');
const navItem_5 = document.querySelector('#nav-item-5');
const navItem_6 = document.querySelector('#nav-item-6');
const navItem_7 = document.querySelector('#nav-item-7');
const navItem_8 = document.querySelector('#nav-item-8');

let pauseButton = document.querySelector('#paus-button');

[].forEach.call(allApps, (app) => {
    app.addEventListener("click", appSelection);
    app.addEventListener("mouseover", mouseOverNavItem);
    app.addEventListener("mouseout", mouseOutNavItem);
});

function switchOnOff() {
    activated = !activated;
    if (activated) {
        pauseButton.innerHTML = "Running";
        pauseButton.style.borderColor = "green";
    } else {
        pauseButton.innerHTML = "Paused";
        pauseButton.style.borderColor = "red";
    }
}

function mouseOverNavItem() {
    /* this.style.height = "4.2rem";
    this.style.width = "4.2rem"; */
    this.style.cssText += "font-size: 2rem;"
    /* this.style. */
}

function mouseOutNavItem() {
    /* this.style.height = "4rem";
    this.style.width = "4rem"; */
    this.style.cssText += "font-size: x-large;"
    /* this.style.backgroundColor = "rgba(44, 84, 193, 0.715)"; */
}

// 0 - 1 * -1 - 1
function getRandom(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
    /* let calc =  Math.floor(Math.random() * max);
    if(Math.floor(Math.random() * 1) */
}

/* balls_1.addEventListener("click", appSelection);
navItem_2.addEventListener("click", appSelection);
navItem_3.addEventListener("click", appSelection);
navItem_4.addEventListener("click", appSelection);
navItem_5.addEventListener("click", appSelection);
navItem_6.addEventListener("click", appSelection);
navItem_7.addEventListener("click", appSelection);
navItem_8.addEventListener("click", appSelection); */

function setCurrentApp(appNumber) {
    switch (appNumber) {
        case 'nav-item-1':
            states.balls_1 = true;
            canvasSectionH1.innerHTML = "Colliding Balls";
            canvasSectionH2.innerHTML = "Interact with mouse, move and click."
            break;
        case 'nav-item-2':
            runPaint2Init = false;
            states.paint = true;
            canvasSectionH1.innerHTML = "Paint in black & white";
            canvasSectionH2.innerHTML = "Interact with mouse, move and click."
            break;
        case 'nav-item-3':
            runPaint3Init = false;
            states.nav_3 = true;
            canvasSectionH1.innerHTML = "Color brush";
            canvasSectionH2.innerHTML = "Interact with mouse, move and click."
            break;
        case 'nav-item-4':
            runPaint4Init = false;
            states.nav_4 = true;
            canvasSectionH1.innerHTML = "Random lines";
            canvasSectionH2.innerHTML = "Interact by mouse clicking."
            break;
        case 'nav-item-5':
            states.nav_5 = true;
            canvasSectionH1.innerHTML = "Canvas 5";
            canvasSectionH2.innerHTML = "Not implemented."
            break;
        case 'nav-item-6':
            states.nav_6 = true;
            canvasSectionH1.innerHTML = "Canvas 6";
            canvasSectionH2.innerHTML = "Not implemented."
            break;
        case 'nav-item-7':
            states.nav_7 = true;
            canvasSectionH1.innerHTML = "Canvas 7";
            canvasSectionH2.innerHTML = "Not implemented."
            break;
        case 'nav-item-8':
            states.nav_8 = true;
            canvasSectionH1.innerHTML = "Canvas 8";
            canvasSectionH2.innerHTML = "Not implemented."
            break;
    }
}

function setAllStatesOff() {
    /*  for (const [key, value] of Object.entries(states)) {
         key.value = false;
         console.log(key, value);
       } */
    /*       states.forEach((value, key, map) => map.set(key, false));
     */
    states = {
        balls_1: false,
        paint: false,
        nav_3: false,
        nav_4: false,
        nav_5: false,
        nav_6: false,
        nav_7: false,
        nav_8: false
    };

    [].forEach.call(allApps, (app) => {
        /* app.style.color = "white"; */
        app.style.backgroundColor = 'rgba(44, 84, 193, 0.715)';
    });

    /* states.balls_1 = false; 
    states.nav_2 = false;
    states.nav_3 = false;
    states.nav_4 = false;
    states.nav_5 = false;
    states.nav_6 = false;
    states.nav_7 = false;
    states.nav_8 = false; */
}

/* function setCurrentAppCSS(nav){
    nav.style.background = "Yellow";
} */

function appSelection() {
    /* console.log(this.innerHTML); */
    /* console.log(this.id + " id"); */
    setAllStatesOff();
    setCurrentApp(this.id);
    let item = document.querySelector("#" + this.id);
    /* console.log(item); */
    this.style.backgroundColor = "green";
    /* item.style.backgroundColor = 'rgba(44, 84, 193, 0.715)'; */
    /* item.style.color = "white"; */
    /* setCurrentAppCSS(this.id); */
}

let appBallsInit = false;
let balls = [];
let playerBall;

function getBall() {
    /* return new Ball(canvas.width/2, canvas.height/2, getRandom(-1, 1), getRandom(-1, 1), "rgba(30,30,30,1", 5); */
    return new Ball(canvas.width / 2, canvas.height / 2, 10);
}

function runAppBalls() {
    console.log("Current app: " + "Balls");

    if (!appBallsInit) {
        playerBall = new Ball(canvas.width / 2, canvas.height / 2, 20);
        playerBall.color = "rgb(20,40,225)";
        balls.push(playerBall);

        for (let index = 0; index < 5; index++) {
            /* const element = array[index]; */
            const ball = getBall();
            balls.push(ball);
        }
        appBallsInit = true;
    }

    ctx.clearRect(
        0, 0,
        canvas.width,
        canvas.height
    );

    ctx.beginPath();
    ctx.fillStyle = 'gray';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fill();

    balls.forEach(ball => {
        ball.update();
    });

}

let runPaint2Init = false;
let runPaint3Init = false;

function runPaint2() {
    if (!runPaint2Init) {
        ctx.clearRect(
            0, 0,
            canvas.width,
            canvas.height
        );
        ctx.beginPath();
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fill();

        runPaint2Init = true;
    }

    ctx.beginPath();
    /* ctx.fillStyle = this.color; */
    ctx.arc(mouseOnCanvasX, mouseOnCanvasY, 15, 0, 2 * Math.PI);
    ctx.fill();
}

let app3ColorR = 255;
let app3ColorG = 255;
let app3ColorB = 100;

function runApp3() {

    if (!runPaint3Init) {
        ctx.clearRect(
            0, 0,
            canvas.width,
            canvas.height
        );
        ctx.beginPath();
        ctx.fillStyle = 'black';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fill();

        runPaint3Init = true;
    }

    /* ctx.save(); */

    for (let i = 0; i < 6; i++) {
        for (let j = 0; j < 6; j++) {
            ctx.fillStyle = `rgba(
              ${Math.floor(app3ColorR - 42.5 * i)},
              ${Math.floor(app3ColorG - 42.5 * j)},
              ${app3ColorB},
              ${getRandom(0, 1)})`;
            ctx.fillRect(mouseOnCanvasX - j * 25 + 50,
                mouseOnCanvasY - i * 25 + 50,
                25, 25);
        }
    }

    /*  ctx.restore(); */


    /* ctx.fillStyle = 'orange'; */


}

let runPaint4Init = false;
let paint4X = 0;
let paint4Y = 0;


function runApp4() {
    if (!runPaint4Init) {
        ctx.clearRect(
            0, 0,
            paint4X,
            paint4Y
        );
        ctx.beginPath();
        ctx.fillStyle = 'rgb(225,225,225)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fill();
        ctx.moveTo(canvas.width / 2, canvas.height / 2);
        runPaint4Init = true;
        paint4X = canvas.width / 2;
        paint4Y = canvas.height / 2;
    }

    ctx.beginPath();
    /* ctx.moveTo(20, 20); */
    ctx.lineTo(paint4X, paint4Y);
    let amount = getRandom(1, 10);
    paint4X += getRandom(-amount, amount);
    paint4Y += getRandom(-amount, amount);
    if (paint4X > canvas.width) {
        paint4X = canvas.width;
    }
    if (paint4X < 0) {
        paint4X = 0;
    }

    if (paint4Y > canvas.height) {
        paint4Y = canvas.height;
    }
    if (paint4Y < 0) {
        paint4Y = 0;
    }

    ctx.lineWidth = getRandom(1, 1.5);
    ctx.lineTo(paint4X, paint4Y);
    /* ctx.lineTo(70, 100); */
    ctx.strokeStyle = "blue";
    ctx.stroke();


}

function runApp5() {
    ctx.clearRect(
        0, 0,
        canvas.width,
        canvas.height
    );

    ctx.beginPath();
    ctx.fillStyle = 'green';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fill();
}

function runApp6() {
    ctx.clearRect(
        0, 0,
        canvas.width,
        canvas.height
    );

    ctx.beginPath();
    ctx.fillStyle = 'LightCyan';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fill();
}

function runApp7() {
    ctx.clearRect(
        0, 0,
        canvas.width,
        canvas.height
    );

    ctx.beginPath();
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fill();
}

function runApp8() {
    ctx.clearRect(
        0, 0,
        canvas.width,
        canvas.height
    );

    ctx.beginPath();
    ctx.fillStyle = 'red';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fill();
}

function runContent() {
    if (states.balls_1) {
        runAppBalls();
    } else if (states.paint) {
        runPaint2();
        console.log("2");
    }
    else if (states.nav_3) {
        runApp3();
        console.log("3");
    }
    else if (states.nav_4) {
        runApp4();
        console.log("4");
    }
    else if (states.nav_5) {
        runApp5();
        console.log("5");
    }
    else if (states.nav_6) {
        runApp6();
        console.log("6");
    }
    else if (states.nav_7) {
        runApp7();
        console.log("7");
    }
    else if (states.nav_8) {
        runApp8();
        console.log("8");
    }
}

let maxFPS = 100;

let fpsCounter = 0;

function run() {
    if (activated) {
        fpsCounter += 1; // når 100 efter 1 sekund
        // >= 100 vid 1 fps
        // >= 50 vid 
        // 96 fps ska man vänta 4 fps
        // MaxFPS = 100. FPS = 96. 
        /* if(fpsCounter > (maxFPS - fps)){ */
        if (fpsCounter > (maxFPS - fps)) {
            runContent();
            /* console.log(fps); */
            fpsCounter = 0;
        }
        /* setTimeout(runContent(), 100000); */
        /* console.log(fps); */
    }
}

setInterval(run, 4 /*4 is minimum 10 1000 / maxFPS */);


let states = {
    balls_1: false,
    paint: false,
    nav_3: false,
    nav_4: false,
    nav_5: false,
    nav_6: false,
    nav_7: false,
    nav_8: false
};

class Shape {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.velX = 5;
        this.velY = 5;
        this.color = 'rgba(0,0,0,1)';
    }
}

class Ball extends Shape {
    // return new Ball(canvas.width/2, canvas.height/2, getRandom(-1, 1), getRandom(-1, 1), "rgba(30,30,30,1", 5);
    constructor(x, y, size) {
        super(x, y);
        this.size = size;
        this.velX = getRandom(-4, 4);
        this.velY = getRandom(-4, 4);
    }

    draw() {
        ctx.beginPath();
        ctx.fillStyle = this.color;
        ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
        ctx.fill();
    }

    move() {
        this.x += this.velX;
        this.y += this.velY;
    }

    outOfBoundsCheck() {
        if (this.x > canvas.width) {
            this.x -= canvas.width / 10;
        }
        if (this.x < 0) {
            this.x += canvas.width / 10;
        }
        if (this.y > canvas.height) {
            this.y -= canvas.height / 10;
        }
        if (this.y < 0) {
            this.y += canvas.height / 10;
        }
    }

    collisionDetect() {
        for (const ball of balls) {
            if (!(this === ball)) {
                const dx = this.x - ball.x;
                const dy = this.y - ball.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < this.size + ball.size) {
                    /* ball.color = this.color = randomRGB(); */
                    ball.x += getRandom(-1, 1);
                    ball.y += getRandom(-1, 1);
                    ball.velX *= -1;
                    ball.velY *= -1;
                    ball.size += getRandom(-1, 1);
                    if (ball.size < 5 || ball.size > 15) {
                        ball.size = 10;
                    }
                }
            }
        }
    }

    update() {
        this.draw();
        this.move();
        this.collisionDetect();
        this.outOfBoundsCheck();
        let collision = false;

        if ((this.x + this.size) >= canvas.width/* window.innerWidth */) {
            this.velX = -(this.velX);
            collision = true;
        }

        if ((this.x - this.size) <= 0) {
            this.velX = -(this.velX);
            collision = true;
        }

        if ((this.y + this.size) >= canvas.height) {
            this.velY = -(this.velY);
            collision = true;
        }

        if ((this.y - this.size) <= 0) {
            this.velY = -(this.velY);
            collision = true;
        }

        this.x += this.velX;
        this.y += this.velY;

        if (collision) {

        }
    }
}

function getMousePos(canvas, evt) {
    var rect = canvas.getBoundingClientRect(), // abs. size of element
        scaleX = canvas.width / rect.width,    // relationship bitmap vs. element for X
        scaleY = canvas.height / rect.height;  // relationship bitmap vs. element for Y

    return {
        x: (evt.clientX - rect.left) * scaleX,   // scale mouse coordinates after they have
        y: (evt.clientY - rect.top) * scaleY     // been adjusted to be relative to element
    }
}

function handleMouseCoords(event) {

    let mousePos = getMousePos(canvas, event);


    if (userInputAllowed && mouseIsInCanvas) {
        mouseOnCanvasX = mousePos.x;
        mouseOnCanvasY = mousePos.y;

        if (appBallsInit) {
            playerBall.x = mousePos.x;
            playerBall.y = mousePos.y;
            playerBall.velX = 0;
            playerBall.velY = 0;
        }


    }

    if (timestamp === null) {
        timestamp = Date.now();
        lastMouseX = event.clientX;
        lastMouseY = event.clientY;
        return;
    }

    let now = Date.now();
    let dt = now - timestamp;
    let dx = event.clientX - lastMouseX;
    let dy = event.clientY - lastMouseY;
    mouseSpeedX = Math.round(dx / dt * 100);
    mouseSpeedY = Math.round(dy / dt * 100);

    timestamp = now;
    lastMouseX = event.clientX;
    lastMouseY = event.clientY;

}

function userInteruptCheck() {
    userInputAllowed = true;
    /* console.log("userInputAllowed is true"); */
}

function handleMouseDown(event) {
    if (states.balls_1) {
        const ball = new Ball(event.clientX, event.clientY, 13);
        ball.color = "orange";
        balls.push(ball);
    }
    else if (states.paint) {
        ctx.fillStyle = "rgb(0,0,0)";

    }
    else if (states.nav_3) {

        app3ColorR = getRandom(0, 255);
        app3ColorG = getRandom(0, 255);
        app3ColorB = getRandom(0, 255);
    }
    else if (states.nav_4) {

        ctx.beginPath();
        ctx.moveTo(paint4X, paint4Y);
        paint4X = mouseOnCanvasX;
        paint4Y = mouseOnCanvasY;
        ctx.lineWidth = getRandom(3, 5);
        ctx.lineTo(paint4X, paint4Y);
        const randomColor = Math.floor(Math.random() * 16777215).toString(16);
        ctx.strokeStyle = "#" + randomColor;
        ctx.stroke();
        /* let amount = getRandom(1,5); */
        /* paint4X += getRandom(-amount,amount);
        paint4Y += getRandom(-amount,amount); */
    }
}

function handleMouseUp(event) {
    if (paint_2) {
        ctx.fillStyle = "rgb(255,255,255)";
    }
}

let mouseIsInCanvas = false;

function handleMouseEnter(event) {
    mouseIsInCanvas = true;
}

function handleMouseLeave(event) {
    mouseIsInCanvas = false;
    if (states.balls_1) {
        playerBall.velX = getRandom(-1, 1);
        playerBall.velY = getRandom(-1, 1);
    }
}

canvas.onmouseenter = handleMouseEnter;
canvas.onmouseleave = handleMouseLeave;

canvas.onmousedown = handleMouseDown;
canvas.onmouseup = handleMouseUp;

canvas.onmousemove = handleMouseCoords;

let mouseSpeedX;
let mouseSpeedY;

let timestamp = null;
let lastMouseX = null;
let lastMouseY = null;

var haveEvents = 'ongamepadconnected' in window;
var controllers = {};

function connecthandler(e) {
    addgamepad(e.gamepad);
}

function addgamepad(gamepad) {
    controllers[gamepad.index] = gamepad;

    var d = document.createElement("div");
    d.setAttribute("id", "controller" + gamepad.index);

    var t = document.createElement("h1");
    t.appendChild(document.createTextNode("gamepad: " + gamepad.id));
    d.appendChild(t);

    var b = document.createElement("div");
    b.className = "buttons";
    for (var i = 0; i < gamepad.buttons.length; i++) {
        var e = document.createElement("span");
        e.className = "button";
        //e.id = "b" + i;
        e.innerHTML = i;
        b.appendChild(e);
    }

    d.appendChild(b);

    var a = document.createElement("div");
    a.className = "axes";

    for (var i = 0; i < gamepad.axes.length; i++) {
        var p = document.createElement("progress");
        p.className = "axis";
        //p.id = "a" + i;
        p.setAttribute("max", "2");
        p.setAttribute("value", "1");
        p.innerHTML = i;
        a.appendChild(p);
    }

    d.appendChild(a);

    // See https://github.com/luser/gamepadtest/blob/master/index.html
    var start = document.getElementById("start");
    if (start) {
        start.style.display = "none";
    }

    document.body.appendChild(d);
    requestAnimationFrame(updateStatus);
}

function disconnecthandler(e) {
    removegamepad(e.gamepad);
}

function removegamepad(gamepad) {
    var d = document.getElementById("controller" + gamepad.index);
    document.body.removeChild(d);
    delete controllers[gamepad.index];
}

function updateStatus() {
    if (!haveEvents) {
        scangamepads();
    }

    var i = 0;
    var j;

    for (j in controllers) {
        var controller = controllers[j];
        var d = document.getElementById("controller" + j);
        var buttons = d.getElementsByClassName("button");

        for (i = 0; i < controller.buttons.length; i++) {
            var b = buttons[i];
            var val = controller.buttons[i];
            var pressed = val == 1.0;
            if (typeof (val) == "object") {
                pressed = val.pressed;
                val = val.value;
            }

            var pct = Math.round(val * 100) + "%";
            b.style.backgroundSize = pct + " " + pct;

            if (pressed) {
                b.className = "button pressed";
            } else {
                b.className = "button";
            }
        }

        var axes = d.getElementsByClassName("axis");
        for (i = 0; i < controller.axes.length; i++) {
            var a = axes[i];
            a.innerHTML = i + ": " + controller.axes[i].toFixed(4);
            a.setAttribute("value", controller.axes[i] + 1);
        }
    }

    requestAnimationFrame(updateStatus);
}

function scangamepads() {
    var gamepads = navigator.getGamepads ? navigator.getGamepads() : (navigator.webkitGetGamepads ? navigator.webkitGetGamepads() : []);
    for (var i = 0; i < gamepads.length; i++) {
        if (gamepads[i]) {
            if (gamepads[i].index in controllers) {
                controllers[gamepads[i].index] = gamepads[i];
            } else {
                addgamepad(gamepads[i]);
            }
        }
    }
}

window.addEventListener("gamepadconnected", connecthandler);
window.addEventListener("gamepaddisconnected", disconnecthandler);

if (!haveEvents) {
    setInterval(scangamepads, 500);
}