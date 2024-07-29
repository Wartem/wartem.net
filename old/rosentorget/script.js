/* let myImage = new Image();
myImage.src = 'Assets/Images/entre.jpg'; */
/* document.querySelector('img').src = "Assets/Images/entre.jpg"; */

/* let slideShowImage = document.querySelector('.slideshow-image'); */
let slideShowImage = document.querySelector('.container-main');

let assetsFilePath = "../../Assets/"

let slideShowBackground = assetsFilePath + "Images/";
slideShowBackground += "entre.jpg";
slideShowImage.style.cssText += "background-image: url(\""+ slideShowBackground + "\")";



let seasonImage = assetsFilePath + "Images/Seasons/";
console.log(getSeason());
switch (getSeason()) {
    case 'winter':
        seasonImage = seasonImage.concat("winter.jpg");
        break;
    case 'spring': // white: #f7f7f7
        seasonImage = seasonImage.concat("spring.jpg"); // light green #018f1e #147800 #0e5700
        /* document.querySelector('body').style.cssText += "background: radial-gradient(#bfffb3, #0e5700);" */
        document.querySelector('body').style.cssText += 'background: rgba(169, 253, 176, 0.373)'
        /* "background-color: #147800"; */
        break;
    case 'summer':
        seasonImage = seasonImage.concat("summer.jpg");
        break;
    case 'fall':
        seasonImage = seasonImage.concat("autumn.jpg");
        break;
}

let header = document.querySelector('.container-header');
console.log("background-image: url(\""+ seasonImage + "\")");
header.style.cssText += "background-image: url(\""+ seasonImage + "\")";
header.style.cssText += "background-size: cover;";
header.style.cssText += "background-position: center center;";
header.style.cssText += "background-repeat: no-repeat;";
/* header.style.cssText += "background-attachment: fixed;"; */

let navItems = document.querySelectorAll('.nav-item');

/* navItems.addEventListener('mouseover', () =>{ */

[].forEach.call(navItems, (navItem) => {
    /* console.log(navItems); */

    navItem.addEventListener('mouseover', () => {
        /* console.log("fdfkjkf"); */
        /* box.style = "border-width: 0.3rem"; font-weight: bold; font-size: 1.5rem;  */
       /*  navItem.style.cssText += "color: white;"; */ /* text-shadow: 0.4rem 0.4rem; border-style: groove;*/
        navItem.style.cssText += "text-decoration: underline; text-decoration-thickness: 8%; transition-duration: 200ms;";
        /* navItem.style.cssText += "filter: blur(1px);"; */
        /* navItem.style.cssText += "-webkit-filter: blur(1px);"; */
        /* navItem.style.cssText += "opacity: 0.5;" */
        /* navItem.style.cssText += "font-size: 1.6rem"; */
        navItem.style.cssText += "border-inline: solid; border-width: 0.2rem; border-radius: 2rem;";
    })

    navItem.addEventListener('mouseout', () => {
        /* box.style = "border-width: 0.2rem"; */
        /* navItem.style.cssText = "background: yellow;"; font-weight: bold; font-size: 1.5rem;  */
        navItem.style.cssText += "text-decoration: none; transition-duration: 100ms;";
        navItem.style.cssText += "border-inline: none; border-width: 0";
    })
});

function getSeason(){
    const date = new Date();
    let season;
    /* console.log(date.getMonth()) */
    switch(date.getMonth() + 1){
        case 12:
            case 1:
            case 2:
                season = 'winter';
                break;
            case 3:
            case 4:
            case 5:
                season = 'spring';
                break;
            case 6:
            case 7:
            case 8:
                season = 'summer';
                break;
            case 9:
            case 10:
            case 11:
                season = 'fall';
                break;
        }
        /* console.log(season); */
        return season;
    }

    let slideShowImages = ["entre.jpg",
    "entre_konsthall_tjornedala.jpg",
    "frukost2.jpg",
    "hus_solnedgang.jpg",
    "I_skuggan_under_bladverket.JPG",
    "easter.jpg",
    "ros.jpg",
    "spring_flowers.jpg",
    "white_spring_flowers.jpg"
    /* "avlångt_format_rosträdgård.jpg" */
    ];

    let imageElement = document.querySelector('.slideshow-image img');

    let currentSlideShowImageIndex = 0;

    function switchInSlideShow(){

      /*   imageElement.style.cssText = "max-width: 50rem";
        imageElement.style.cssText += "min-width: 10rem";
        imageElement.style.cssText += "max-width: 60%";
        imageElement.style.cssText += "max-height: 80%";
        imageElement.style.cssText += "height: auto";
        imageElement.style.cssText += "border-radius: 1rem";
        imageElement.style.cssText += "border-style: ridge";
        imageElement.style.cssText += "border-width: 0.5rem";
        imageElement.style.cssText += "border-color: rgba(253, 252, 169, 0.356)"; */

        
        imageElement.src = assetsFilePath + "Images/" + slideShowImages[currentSlideShowImageIndex];
        /* imageElement.style.cssText += "animation: fade-in 3s linear infinite 500ms"; */
        
        imageElement.style.cssText += "animation-name: fade-in;";
        imageElement.style.cssText += "animation-duration: 5s;";
        /* imageElement.style.cssText += "animation-delay: 0.5s;"; */
        imageElement.style.cssText += "animation-iteration-count: infinite";
        imageElement.style.cssText += "animation-fill-mode: backwards";
        
  /*       imageElement.style.cssText += "opacity: 0;" */

        currentSlideShowImageIndex ++;
        if(currentSlideShowImageIndex >= slideShowImages.length){
            currentSlideShowImageIndex = 0;
        }
    }

    /* var start = new Date().getTime();
    var end = new Date().getTime();
    var time = end - start; */

    setInterval(switchInSlideShow, 5000);