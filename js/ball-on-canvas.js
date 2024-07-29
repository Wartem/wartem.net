let canvas = document.querySelector('#canvas');
const ctx = canvas.getContext('2d');
ctx.fillStyle = 'rgba(0, 0, 0, 0.80)';
ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);

canvas.width = window.innerWidth;//2000;
canvas.height = window.innerHeight;//1000;

let mouseOnCanvasX = canvas.width/2;
let mouseOnCanvasY = canvas.height/2;

class Shape {

    constructor(x, y, velX, velY) {
      this.x = x;
      this.y = y;
      this.velX = velX;
      this.velY = velY;
    }
  
  }

class Ball extends Shape {

    constructor(x, y, velX, velY, color, size) {
      super(x, y, velX, velY);
  
      this.color = color;
      this.size = size;
      this.exists = true;
    }
  
    draw() {

        ctx.beginPath();
        ctx.fillStyle = this.color;
        ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
        ctx.fill();
  
      /* ctx.translate(0, -radius*0.85); */
     /*  ctx.beginPath(); */
      /* ctx.fillStyle = `rgba(
        ${backgroundR},
        ${backgroundG},
        ${backgroundB},
        ${backGroundA});`; */
     /*    rgba(123,42,145,0.8)
      ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI); */
      
    /*   ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillRect(0, 0, canvas.width, canvas.height); */
   /*  ctx.stroke();
    ctx.fill(); */
     /*  ctx.restore(); */

     
    }



    /* collisionDetect(){
        for (const ball of balls) {
            if (!(this === ball) && ball.exists) {
               const dx = this.x - ball.x;
               const dy = this.y - ball.y;
               const distance = Math.sqrt(dx * dx + dy * dy);
    
               if (distance < this.size + ball.size) {
                 ball.color = this.color = randomRGB();
                 ball.velX *=-1;
                 ball.velY *=-1;
               }
            }
         }
        }   */

        

        update() {
            this.draw();

            /* this.velX = mouseSpeedX;
            this.velY = mouseOnCanvasY; */

            

            let collision = false;

            if ((this.x + this.size) >= window.innerWidth) {
              this.velX = -(this.velX);
              collision = true;
            }
        
            if ((this.x - this.size) <= 0) {
              this.velX = -(this.velX);
              collision = true;
            }
        
            if ((this.y + this.size) >= window.innerHeight) {
              this.velY = -(this.velY);
              collision = true;
            }
        
            if ((this.y - this.size) <= 0) {
              this.velY = -(this.velY);
              collision = true;
            }

            
        
            this.x += this.velX;
            this.y += this.velY;

            if(collision){
              
                /* console.log("collision"); */
                /* userInputAllowed = false;
                setTimeout(userInteruptCheck, 5000); */
                /* setTimeout(()=>userInputAllowed = true, 2000); */
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

  let timestamp = null;
  let lastMouseX = null;
let lastMouseY = null;
let mouseSpeedX;
let mouseSpeedY;

  function handleMouseCoords(event){

    let pos = getMousePos(canvas, event);
    mouseOnCanvasX = pos.x;
    mouseOnCanvasY = pos.y;

   /*  playerBall.x = mouseOnCanvasX;
    playerBall.y = mouseOnCanvasY; */

    // ---------------------------------------
    // https://stackoverflow.com/questions/6417036/track-mouse-speed-with-js

    if (timestamp === null) {
        timestamp = Date.now();
        lastMouseX = event.clientX;
        lastMouseY = event.clientY;
        return;
    }

    let now = Date.now();
    let dt =  now - timestamp;
    let dx = event.clientX - lastMouseX;
    let dy = event.clientY - lastMouseY;
    mouseSpeedX = Math.round(dx / dt * 100);
    mouseSpeedY = Math.round(dy / dt * 100);

    timestamp = now;
    lastMouseX = event.clientX;
    lastMouseY = event.clientY;
  }

    /* var mrefreshinterval = 500; // update display every 500ms
    var lastmousex=-1; 
    var lastmousey=-1;
    var lastmousetime;
    var mousetravel = 0;
    $('html').mousemove(function(e) {
        var mousex = e.pageX;
        var mousey = e.pageY;
        if (lastmousex > -1)
            mousetravel += Math.max( Math.abs(mousex-lastmousex), Math.abs(mousey-lastmousey) );
        lastmousex = mousex;
        lastmousey = mousey;
    });
  } */

  function mouseLeavingCanvas(){
    mouseOnCanvasX = canvas.width/2;
    mouseOnCanvasY = canvas.height/2;
  }

  canvas.addEventListener ("mouseout", mouseLeavingCanvas, false);
  let partOfX = mouseOnCanvasX/canvas.width;
  let partOfY = mouseOnCanvasY/canvas.height;

  function run(){

    partOfX = mouseOnCanvasX/canvas.width;
    partOfY = mouseOnCanvasY/canvas.height;

    let backgroundR = 126;
    let backgroundG = 172;
    let backgroundB = /* 194 */ 150 + 90 * partOfX * playerBall.x/canvas.width; 
    let backGroundA = 0.43 + 0.5 * partOfY * playerBall.y/canvas.height;

    playerBall.color = "rgb(20,"+/* playerBall.x/canvas.width */+
    playerBall.y/canvas.height*
    180 + ",180)";

    playerBall.size = 20 + 50 * (playerBall.x/canvas.width);

    

  ctx.beginPath();
  /* ctx.fillStyle = 'rgba(123,42,145,0.8)'; */
  ctx.fillStyle = `rgba(
      ${backgroundR},
      ${backgroundG},
      ${backgroundB},
      ${backGroundA})`;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fill();

  /* console.log(mouseOnCanvasX); */

  playerBall.update();
  }

  function run2(){
    
    /* 'rgba('+mouseSpeedX'0, 0, 0, 0.50)'; */
    /* ctx.fillRect(0, 0, window.innerWidth, window.innerHeight); */

    
    /* ctx.save();
    ctx.clearRect(0, 0, canvas.width, canvas.height); */
    /* ctx.beginPath(); */
    /* ctx.fillStyle = this.color; */
    /* ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI); */
    /* ctx.stroke(); */
    /* ctx.fillRect(0, 0, canvas.width, canvas.height); */
    /* ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fill(); */
    /* ctx.restore(); */

    if(mouseOnCanvasX > 1 && mouseOnCanvasY > 1){
        const partOfX = mouseOnCanvasX+0.1/canvas.width;
    const partOfY = mouseOnCanvasY+0.1/canvas.height;

    canvas.style.removeProperty('border-left');
    canvas.style.removeProperty('border-right');
    canvas.style.removeProperty('border-top');
    canvas.style.removeProperty('border-bottom');
    canvas.style.removeProperty('border-color');
    canvas.style.removeProperty('border-style');

  /*   let borderRight = (canvas.width - partOfX*canvas.width);
    let borderDown = (canvas.height - partOfY*canvas.height); */
    /* canvas.style.cssText += "border-color: yellow;"; */

    
    canvas.style.cssText += "border-left: "+partOfX+"px;";
    /* canvas.style.cssText += "border-right: "+borderRight+"px;"; */

    canvas.style.cssText += "border-top: "+-partOfY+"px;";
    /* canvas.style.cssText += "border-bottom: "+borderDown+"px; "; */
    canvas.style.cssText += "border-color: #034463; border-style: solid;";

      let backgroundR = 126;
      let backgroundG = 172;
      let backgroundB = 194 + 50 * partOfX; 
      let backGroundA = 0.43 + 0.5 * partOfY;

    ctx.beginPath();
    /* ctx.fillStyle = 'rgba(123,42,145,0.8)'; */
    ctx.fillStyle = `rgba(
        ${backgroundR},
        ${backgroundG},
        ${backgroundB},
        ${backGroundA})`;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fill();
    }
 
    

    /* ctx.beginPath();
      ctx.fillStyle = this.color;
      ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
      ctx.fill(); */
    

    playerBall.update();
}

window.onresize = function(){
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight; 
    playerBall.x = canvas.width/2;
    playerBall.y = canvas.height/2;
    /* playerBall = new Ball(canvas.width/2,canvas.height/2,5,5,`rgb(20,40,225)`, 30); */
}

canvas.onmousemove = handleMouseCoords;

  let playerBall = new Ball(canvas.width/2,canvas.height/2,5,5,`#74a591`, 30); //rgb(20,40,225)

  setInterval(run, 10);