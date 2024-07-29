document.addEventListener('keypress', function (e) {
    if (e.keyCode === 13 || e.which === 13) {
        e.preventDefault();
        return false;
    }
});
/* 
transition: .2s ease-in;
  opacity: 0.8; */

var itemList = document.getElementById('items');
var filter = document.getElementById('filter');

filter.addEventListener('keyup', getImages);
itemList.addEventListener('click', removeItem);

/* let js = document.createElement("script");
js.type = "text/javascript";
js.src = "../js/vadskabort.js";
document.body.appendChild(js);
 */

// Add Image
function addItem(newItem){
  
    // Get input value
    /* var newItem = '/images/pic/ducks/duck-5159745_960_720.jpg'; */

    //newItem = "/images/pic/ducks/mallard-3478011_1920.jpg";
    
   console.log(newItem);
    // Create new li element
    var li = document.createElement('li');
    // Add class
    li.className = 'list-group-item';
    // Add text node with input value
    //li.appendChild(document.createTextNode(newItem));

    let img = document.createElement('img');
    img.src = newItem;
    li.appendChild(img);
  
    // Create del button element
    var deleteBtn = document.createElement('button');
  
    // Add classes to del button
    deleteBtn.className = 'btn btn-danger btn-sm float-right delete';
  
    // Append text node
    deleteBtn.appendChild(document.createTextNode('X'));
  
    // Append button to li
    li.appendChild(deleteBtn);
  
    // Append li to list
    itemList.appendChild(li);
   
  }

  // Remove item
function removeItem(e){
    if(e.target.classList.contains('delete')){
      if(confirm('Are You Sure?')){
        var li = e.target.parentElement;
        itemList.removeChild(li);
      }
    }
  }

  function removeAllChildren(theParent){

    // Create the Range object
    var rangeObj = new Range();

    // Select all of theParent's children
    rangeObj.selectNodeContents(theParent);

    // Delete everything that is selected
    rangeObj.deleteContents();
}

  function getImages(e){
    e.preventDefault();

    removeAllChildren(itemList);
    
    var newItem = document.getElementById('item').value;


    for(let i = 0; i < imageArray.length; i++){
        if(newItem.length > 2 && imageArray[i].includes(newItem)){
            addItem(".."+imageArray[i]);
            //console.log(".."+imageArray[i]);
            // /images/pic/ducks/mallard-3478011_1920.jpg
        }
    }
   
  }

  const imageArray = [
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
    "/images/pic/ducks/ducks-5820051_1920.jpg",

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
      "/images/pic/dogs/puppy-1903313_1920.jpg",

      "/images/pic/gott.jpg",
      "/images/pic/gott2.jpg"
    ];