

let seasonImage = "/Assets/Images/Seasons/";
console.log(getSeason());
switch (getSeason()) {
    case 'winter':
        seasonImage = seasonImage.concat("winter.jpg");
        break;
    case 'sprinfg': // white: #f7f7f7
        seasonImage = seasonImage.concat("spring.jpg"); // light green #018f1e #147800 #0e5700
        /* document.querySelector('body').style.cssText += "background: radial-gradient(#bfffb3, #0e5700);" */
        document.querySelector('body').style.cssText += "background-color: #0e5700";
        break;
    case 'summer':
        seasonImage = seasonImage.concat("summer.jpg");
        break;
    case 'fall':
        seasonImage = seasonImage.concat("fall.jpg");
        break;
}

/* let mainMenuDiv = document.createElement("div"); */

/* mainMenuDiv.classList.add('main-menu-div-surface'); */
/* mainMenuDiv.style.cssText += "width: 90%; height: auto; background-color: black;"
mainMenuDiv.style.cssText += "border-style: solid; border-width: 1rem;"
mainMenuDiv.style.cssText += "alight-items: center; align-self: center;"
mainMenuDiv.style.cssText +=  */


/* document.querySelector('.main-menu').appendChild(mainMenuDiv); */

/* document.querySelector('.main-menu').style.cssText += "display: none"; */

/* background-image: url("paper.gif"); */

let header = document.querySelector('.header-div');
/* header.style.opacity = "0.5"; */

console.log("background-image: url(\""+ seasonImage + "\")");
header.style.cssText += "background-image: url(\""+ seasonImage + "\")";
header.style.cssText += "background-size: cover;";

let navItems = document.querySelectorAll('.nav-item');

/* navItems.addEventListener('mouseover', () =>{ */

[].forEach.call(navItems, (navItem) => {
    /* console.log(navItems); */

    navItem.addEventListener('mouseover', () => {
        /* console.log("fdfkjkf"); */
        /* box.style = "border-width: 0.3rem"; font-weight: bold; font-size: 1.5rem;  */
       /*  navItem.style.cssText += "color: white;"; */ /* text-shadow: 0.4rem 0.4rem; border-style: groove;*/
        navItem.style.cssText += "text-decoration: underline; text-decoration-thickness: 5%; transition-duration: 100ms;"
    })

    navItem.addEventListener('mouseout', () => {
        /* box.style = "border-width: 0.2rem"; */
        /* navItem.style.cssText = "background: yellow;"; font-weight: bold; font-size: 1.5rem;  */
        navItem.style.cssText += "text-decoration: none; transition-duration: 100ms;"
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


/* function getSeason() {
    month = document.forms.date.month.value;
    season = '';
    switch (month) {
        case '12':
        case '1':
        case '2':
            season = 'winter';
            break;
        case '3':
        case '4':
        case '5':
            season = 'spring';
            break;
        case '6':
        case '7':
        case '8':
            season = 'summer';
            break;
        case '9':
        case '10':
        case '11':
            season = 'fall';
            break;
    }
    console.log(season);
} */