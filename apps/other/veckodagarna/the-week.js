$(document).ready(function(){
   /*  $(".day").click(function(event){
        let clickebtn = event.id;
        /* console.log(clickebtn.document.html()); */
        //console.log(clickebtn);
    //});
    
    $('.day').on('click', function(e) {
       /*  $("#test"). */

       $(this).css("opacity", "0.4");
       $(this).css("border-color", "black");
       $(this).css("border-style", "solid");

       /* $(this).css("border-width", "5rem"); */
       setTimeout( () => {
        $(this).css("opacity", "1");
        $(this).css("border-width", "0");
       /*  $(this).css("margin", "100"); */
      /*   $(".image-container img").css("pointer-events", "initial"); */
       /*  animIsPlaying = false; */
       }, 1000);

       var text = $(this)/* .attr('id') */.text();
       /* $('#message').val(); */
       var msg = new SpeechSynthesisUtterance();
       var voices = window.speechSynthesis.getVoices();
       msg.voice = voices[$('#voices').val()];
       msg.rate = $('#rate').val() / 10;
       msg.pitch = $('#pitch').val();
       msg.text = text;
 
       msg.onend = function(e) {
         console.log('Finished in ' + event.elapsedTime + ' seconds.');
       };
 
       speechSynthesis.speak(msg);



       
       console.log($(this)/* .attr('id') */.text());
       /*  console.log(e.target.id); */
      });

   
});

$(function(){
    if ('speechSynthesis' in window) {
      speechSynthesis.onvoiceschanged = function() {
        var $voicelist = $('#voices');
  
        if($voicelist.find('option').length == 0) {
          speechSynthesis.getVoices().forEach(function(voice, index) {
            var $option = $('<option>')
            .val(index)
            .html(voice.name + (voice.default ? ' (default)' :''));
  
            $voicelist.append($option);
          });
  
          $voicelist.material_select();
        }
      }
  
    /*   $('#speak').click(function(){
        var text = $('#message').val();
        var msg = new SpeechSynthesisUtterance();
        var voices = window.speechSynthesis.getVoices();
        msg.voice = voices[$('#voices').val()];
        msg.rate = $('#rate').val() / 10;
        msg.pitch = $('#pitch').val();
        msg.text = text;
  
        msg.onend = function(e) {
          console.log('Finished in ' + event.elapsedTime + ' seconds.');
        };
  
        speechSynthesis.speak(msg);
        
      }) */
    } else {
      $('#modal1').openModal();
    }
  });

/* $(document).on("click",".appDetails", function () {
    console.log("hsdjskd");
    var clickedBtnID = $(this).attr('id'); 
    alert('you clicked on button #' + clickedBtnID);
    console.log('you clicked on button #' + clickedBtnID);
 }); */

 /* document.getElementById("points").innerHTML */