console.log("Init");

// let imageContainers = document.getElementsByTagName('img');
//const imageContainers = document.querySelectorAll(".image-container");
// const images = importAll(require.context('../images/Pic', false, /\.(png|jpe?g|svg)$/));

const Dog = 0;
const Duck = 1;
let points = 0;

let currentOddAnimal = "";
let usedImages = [];

const imageContainers = document.getElementsByTagName("img");

function getRandomIMGIndex(){
  return Math.floor(Math.random() * imageContainers.length);
}

function getRandomAnimalType(){
  return Math.floor(Math.random() * 2);
}

function runGame(){
  let animalType = getRandomAnimalType();
  let randomIMGIndex = getRandomIMGIndex();

  console.log(randomIMGIndex + " :::::::: randomIMGIndex");

  if(animalType === Dog){
    currentOddAnimal = getRandomDuckImage();
  }else{
    currentOddAnimal = getRandomDogImage();
  }

  console.log("currentOddAnimal " + currentOddAnimal);

  // Set the odd image
  $(imageContainers[randomIMGIndex]).attr("src", currentOddAnimal);

    usedImages = [];
    // Set the other 3 images / the rest
    for (let i = 0; i < imageContainers.length; i++) {
      if(i !== randomIMGIndex){
       // $(imageContainers[i]).attr("src", getRandomDogImage());
        
        switch (animalType) {
          case Dog:
            console.log("dog added to " + i);
            $(imageContainers[i]).attr("src", getRandomDogImage());
            break;
            case Duck:
              console.log("duck added to " + i);
              $(imageContainers[i]).attr("src", getRandomDuckImage());
              break;
              default:
        }
      }
      }
      usedImages = [];
}


let orginalColor = document.getElementById("outer").style.background;

function highlightBackground(color){
  document.getElementById("outer").style.background = color;
  /* document.body.style.backgroundColor = color; */
  setTimeout(function(){
    document.getElementById("outer").style.background = orginalColor;
  }, 1000);
}

$(document).ready(function(){
  $("img").click(function(){
    //$(this).hide();
  //  let oldImage = $(this).attr("src");
  //  let newImage = getRandomImage();
  //  while(oldImage === newImage){

  if($(this).attr("src") === currentOddAnimal){
   /*  alert("Correct!"); */
   highlightBackground("green");
    points += 1;
  }else{
    highlightBackground("red");
    points -= 1;
  }

  document.getElementById("instructions-text").innerHTML = 
    "Click on the animal that does not fit in with the others. Points: " + points;

  runGame();
});
});

/* function getRandomDogImage(){
  let index = Math.floor(Math.random() * dogImageArray.length);
  console.log("New random dog index: " + index);
  /* usedIndex.forEach(doesArrayContainImageString) */
  /* for(let i = 0; i < usedImages.length; i++){
    if(usedImages[i] === dogImageArray[index]){
      console.log("usedImages["+i+"] === dogImageArray["+index+"] = " + dogImageArray[index]);
      getRandomDogImage();
    }else{
      usedImages.push(dogImageArray[index]);
      return ".." + dogImageArray[index];
    }
  }
  return ".." + dogImageArray[index];
} */ 

function getRandomDogImage(){
  let index = Math.floor(Math.random() * dogImageArray.length);
  console.log("New random dog index: " + index);

  while(usedImages.includes(dogImageArray[index])){
    index = Math.floor(Math.random() * dogImageArray.length);
  }

  usedImages.push(dogImageArray[index]);
  return ".." + dogImageArray[index];
}

function getRandomDuckImage(){
  let index = Math.floor(Math.random() * duckImageArray.length);
  console.log("New random duck index: " + index);

  while(usedImages.includes(duckImageArray[index])){
    index = Math.floor(Math.random() * duckImageArray.length);
  }

  usedImages.push(duckImageArray[index]);
  return ".." + duckImageArray[index];
}

/*   for(let i = 0; i < usedImages.length; i++){

    while(usedImages[i] !== duckImageArray[index]){

    }


    if(usedImages[i] === duckImageArray[index]){
      console.log("usedImages["+i+"] === duckImageArray["+index+"] = " + duckImageArray[index]);
      getRandomDuckImage();
    }else{
      usedImages.push(duckImageArray[index]);
      return ".." + duckImageArray[index];
    }
  }

  return ".." + duckImageArray[index];
} */


   // alert(element);
  // let imageChild = imageContainer.getElementChild
// querySelectorAll()

const duckImageArray = [
  "/images/pic/ducks/mallard-3478011_1920.jpg",
   "/images/pic/ducks/ducks-2655535_1920.jpg",
    "/images/pic/ducks/mallard-3609130_1920.jpg",
   "/images/pic/ducks/mallard-4414758_960_720.jpg",
     "/images/pic/ducks/nile-goose-3538831_960_720.jpg",
    "/images/pic/ducks/duck-5159745_960_720.jpg",
    "/images/pic/ducks/bird-3320548_960_720.jpg",
    "/images/pic/ducks/duck-61679_960_720.jpg",
    "/images/pic/ducks/duck-2028587_960_720.jpg",
    "/images/pic/ducks/mallard-3747770_1920.jpg",
  "/images/pic/ducks/eurasian-wigeon-4914971_1920.jpg",
  "/images/pic/ducks/ruddy-shelduck-106544_1920.jpg",
  "/images/pic/ducks/animal-3824672_1920.jpg",
   "/images/pic/ducks/drake-2028582_1920.jpg",
  "/images/pic/ducks/duck-1884934_1920.jpg",
  "/images/pic/ducks/duck-4077117_1920.jpg",
   "/images/pic/ducks/duck-4924132_1920.jpg",
  "/images/pic/ducks/duck-cub-1508409_1920.jpg",
  "/images/pic/ducks/ducklings-1853178_1920.jpg",
  
  "/images/pic/ducks/ducks-204332_1920.jpg",
  "/images/pic/ducks/ducks-5820051_1920.jpg"
  ];
  
  const dogImageArray = [
    "/images/pic/dogs/adorable-3344414_1920.jpg",
    "/images/pic/dogs/akita-5964180_1920.jpg",
    "/images/pic/dogs/animal-3786987_1920.jpg",
    "/images/pic/dogs/animal-6889575_1920.jpg",
    "/images/pic/dogs/australian-shepherd-6556697_1920.jpg",
    "/images/pic/dogs/dog-287420_1920.jpg",
    "/images/pic/dogs/dog-1168663_1920.jpg",
    "/images/pic/dogs/dog-1194083_1920.jpg",
    "/images/pic/dogs/dog-1194087_1920.jpg",
    "/images/pic/dogs/dog-2561134_1920.jpg",
    "/images/pic/dogs/dog-4118585_1920.jpg",
    "/images/pic/dogs/dog-4608266_1920.jpg",
    "/images/pic/dogs/dog-5793625_1920.jpg",
    "/images/pic/dogs/english-bulldog-562723_1920.jpg",
    "/images/pic/dogs/english-cocker-spaniel-5937757_1920.jpg",
    "/images/pic/dogs/husky-3380548_1920.jpg",
    "/images/pic/dogs/nova-scotia-duck-tolling-retriever-5953883_1920.jpg",
    "/images/pic/dogs/rottweiler-1785760_1920.jpg",
    "/images/pic/dogs/puppy-1903313_1920.jpg"
  ];

  $(document).ready(runGame());