console.log("Init");

const Dog = 0;
const Duck = 1;
let points = 0;

/* let animIsPlaying = false; */

let currentOddAnimal = "";
let usedImages = [];

const imageContainers = document.getElementsByTagName("img");
let audioController = null;

class AudioController {
    constructor() {
        this.flipSound = new Audio('Audio/flip.wav');
        this.correctSound = new Audio('Audio/correct.wav');
        this.failureSound = new Audio('Audio/failure.mp3');
    }

    failure(){
        this.failureSound.play();
    }

    flip() {
        this.flipSound.play();
    }
    correct() {
        this.correctSound.play();
    }
}

function getRandomIMGIndex(){
  return Math.floor(Math.random() * imageContainers.length);
}

function getRandomAnimalType(){
  return Math.floor(Math.random() * 2);
}

function initGame(){
    let animalType = getRandomAnimalType();
  let randomIMGIndex = getRandomIMGIndex();

  if(animalType === Dog){
    currentOddAnimal = getRandomDuckImage();
  }else{
    currentOddAnimal = getRandomDogImage();
  }

  

  // Set the odd image
  $(imageContainers[randomIMGIndex]).attr("src", currentOddAnimal);

    usedImages = [];
    // Set the other 3 images / the rest
    for (let i = 0; i < imageContainers.length; i++) {
      if(i !== randomIMGIndex){
       // $(imageContainers[i]).attr("src", getRandomDogImage());
        
        switch (animalType) {
          case Dog:
         
            $(imageContainers[i]).attr("src", getRandomDogImage());
            break;
            case Duck:
          
              $(imageContainers[i]).attr("src", getRandomDuckImage());
              break;
              default:
        }
      }
      }
      usedImages = [];
}

function runGame(){

  /*   animIsPlaying = true; */
    
   /*  console.log("RunGame"); */

    $(".image-container img").css("pointer-events", "none");
   /*  $(".image-container:hover img").css("transform", "scale(1)"); */
    /* transform: scale(1.05) */


      let heightSaved = $(".image-container img").height();
      $(".image-container img").animate({
      /*  opacity: "1", */
       height: "1rem",
       opacity: "0.1",
       
      }, 200, "swing", function(){
   
        initGame();

        if(Math.floor(Math.random() * 2)){
            $(".image-container img").css("transform", "rotateY(180deg)");
          }


      $(".image-container img").animate({
        /*  opacity: "1", */
         height: heightSaved,
         
        }, 100, "linear",  function(){

      
     
        })  
   }
   );
      

     /*  $(".image-container").css({
        transform: rotateY(-180deg);
      })  */

    /*   setTimeout(function(){
        animIsPlaying = false;
      }, 1300); */

      setTimeout( function(){ 
        $(".image-container img").css("opacity", "1");
        $(".image-container img").css("pointer-events", "initial");
       /*  animIsPlaying = false; */
       }, 1100);
      
}

function _highlightBackground(color){
  document.getElementById("images-frame").style.background = color;
  /* document.body.style.backgroundColor = color; */
  setTimeout(function(){
    document.getElementById("images-frame").style.background = orginalColor;
  }, 1000);
}

let orginalColor = document.getElementById("points").style.background;

function highlightPoints(color){
    document.getElementById("points").style.background = color;
    /* document.body.style.backgroundColor = color; */
    setTimeout(function(){
      document.getElementById("points").style.background = orginalColor;
    }, 1200);
  }

/* $(document).ready(runGame()); */

$(document).ready(function(){
    let audioController = new AudioController();

    if(!$(".image-container img").is(':animated')){
  $(".image-container img").click(function(){
  
   /*  $(this).find(".image-container img").stop(); */

     /* $(this).find(".image-container img").stop(true, true).fadeOut(); */

     /* $(this).find(".image-container img").is
 */
    /* setTimeout(() => turn(), 2000); */

    //$(this).hide();
  //  let oldImage = $(this).attr("src");
  //  let newImage = getRandomImage();
  //  while(oldImage === newImage){

  if($(this).attr("src") === currentOddAnimal){
   /*  alert("Correct!"); */
   //highlightBackground("green");

   highlightPoints("green");
    points += 1;
   audioController.correct(); 
  }else{
    //highlightBackground("red");

    highlightPoints("red");

    points -= 1;
    audioController.failure();
  }

  document.getElementById("points").innerHTML = 
    "Points: " + points;

    runGame();
  
   /*  $("img").slideDown("2000", "linear", runGame());
   */

 /*  turn(); */

});

}


initGame();
 
});

function getRandomDogImage(){
  let index = Math.floor(Math.random() * dogImageArray.length);

  while(usedImages.includes(dogImageArray[index])){
    index = Math.floor(Math.random() * dogImageArray.length);
  }

  usedImages.push(dogImageArray[index]);
  return dogImageArray[index];
}

function getRandomDuckImage(){
  let index = Math.floor(Math.random() * duckImageArray.length);

  while(usedImages.includes(duckImageArray[index])){
    index = Math.floor(Math.random() * duckImageArray.length);
  }

  usedImages.push(duckImageArray[index]);
  return duckImageArray[index];
}

const duckImageArray = [
    "../../images/pic/ducks/mallard-3478011_1920.jpg",
    "../../images/pic/ducks/ducks-2655535_1920.jpg",
     "../../images/pic/ducks/mallard-3609130_1920.jpg",
    "../../images/pic/ducks/mallard-4414758_960_720.jpg",
      "../../images/pic/ducks/nile-goose-3538831_960_720.jpg",
     "../../images/pic/ducks/duck-5159745_960_720.jpg",
     "../../images/pic/ducks/bird-3320548_960_720.jpg",
     "../../images/pic/ducks/duck-61679_960_720.jpg",
     "../../images/pic/ducks/duck-2028587_960_720.jpg",
     "../../images/pic/ducks/mallard-3747770_1920.jpg",
   "../../images/pic/ducks/eurasian-wigeon-4914971_1920.jpg",
   "../../images/pic/ducks/ruddy-shelduck-106544_1920.jpg",
   "../../images/pic/ducks/animal-3824672_1920.jpg",
    "../../images/pic/ducks/drake-2028582_1920.jpg",
   "../../images/pic/ducks/duck-1884934_1920.jpg",
   "../../images/pic/ducks/duck-4077117_1920.jpg",
    "../../images/pic/ducks/duck-4924132_1920.jpg",
   "../../images/pic/ducks/duck-cub-1508409_1920.jpg",
   "../../images/pic/ducks/ducklings-1853178_1920.jpg",
   
   "../../images/pic/ducks/ducks-204332_1920.jpg",
   "../../images/pic/ducks/ducks-5820051_1920.jpg"
   ];
   
   const dogImageArray = [
     "../../images/pic/dogs/adorable-3344414_1920.jpg",
     "../../images/pic/dogs/akita-5964180_1920.jpg",
     "../../images/pic/dogs/animal-3786987_1920.jpg",
     "../../images/pic/dogs/animal-6889575_1920.jpg",
     "../../images/pic/dogs/australian-shepherd-6556697_1920.jpg",
     "../../images/pic/dogs/dog-287420_1920.jpg",
     "../../images/pic/dogs/dog-1168663_1920.jpg",
     "../../images/pic/dogs/dog-1194083_1920.jpg",
     "../../images/pic/dogs/dog-1194087_1920.jpg",
     "../../images/pic/dogs/dog-2561134_1920.jpg",
     "../../images/pic/dogs/dog-4118585_1920.jpg",
     "../../images/pic/dogs/dog-4608266_1920.jpg",
     "../../images/pic/dogs/dog-5793625_1920.jpg",
     "../../images/pic/dogs/english-bulldog-562723_1920.jpg",
     "../../images/pic/dogs/english-cocker-spaniel-5937757_1920.jpg",
     "../../images/pic/dogs/husky-3380548_1920.jpg",
     "../../images/pic/dogs/nova-scotia-duck-tolling-retriever-5953883_1920.jpg",
     "../../images/pic/dogs/rottweiler-1785760_1920.jpg",
     "../../images/pic/dogs/puppy-1903313_1920.jpg"
   ];


   function flipit(){
    /* for (const element of document.getElementsByClassName("image-container")){
        element.style = 
     } */

     /*  $(".image-container").css(
        /* "animation", "flipAll 10s linear infinite 500ms" */
        //"rotate", "rotateY(-180deg)"
      //); */

   
}
   
/* function turnBack(){
     
    $(".image-container img").animate({
     /*  opacity: "1", */
     // height: heightSaved
   /*   }, 2000)
} */ 

/* function turn(){
    
   /*  $("img").animate({transform: '-1.142rad'} , 2000, /*{transform: '-3.142rad'} ) */
/*    let heightSaved = $(".image-container img").height();
   $(".image-container img").animate({
   /*  opacity: "1", */
/*     height: "1px",
    opacity: "0" 
   }, 600, "swing", function(){ */
/* 
    if(Math.floor(Math.random() * 2)){
        $(".image-container").css("transform", "rotateY(180deg)");
      }
 */
 /*    $(".image-container img").animate({
        /*  opacity: "1", */
      /*    height: heightSaved,
         opacity: "1" 
        }, 1300) */
 /* */ 
        
          
/*    }

   );
} */ 

    /* $(".image-container").focus(function(){
        $(this).animate({
            'transform': 'rotateY(3.142rad)'       
        }, 5000, function() {
           /*  $("#navlinks").css('display', 'block'); */
     //   });
    //}); */
   /*  $(".image-container img").css("transition-delay", "1s"); */
   /*  $(".image-container img").css("-webkit-transform", "rotate(180deg)");
    $(".image-container img").css("-moz-transform", "rotateY(180deg)");
    $(".image-container img").css("-o-transform", "rotateY(180deg)"); */
    /* $(".image-container img").css("transition-delay", "1s"); */
    
    
        /* "animation", "flipAll 10s linear infinite 500ms" */
        /* "transform", "rotateY(360deg)" */


/* @-webkit-keyframes blink {
    0% {
      opacity: 0.0
    }
    ;
    100% {
      opacity: 1.0
    }
    ;
  } */


// let orginalColor = document.getElementById("images-frame").style.background;
