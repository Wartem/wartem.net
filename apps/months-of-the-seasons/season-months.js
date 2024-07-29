


/* () => { */
 
    console.log("1");

$(function(){
   /*  $(document).ready(function(){ */
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
  
    } else {
      $('#modal1').openModal();
    }
  });

  function readText(text) {
    var msg = new SpeechSynthesisUtterance();
    msg.text = text;
    speechSynthesis.speak(msg);
  }

  function readText2(text){
    /* var index = $(this).data().order;
    var text = data[index].title; */

    var msg = new SpeechSynthesisUtterance();
          var voices = window.speechSynthesis.getVoices();
          /* msg.voice = voices[$('#voices').val()]; */
          msg.rate = 1; /* $('#rate').val() / 10; */
          msg.pitch = 1;/* $('#pitch').val(); */
          msg.text = text;
    
          msg.onend = function(e) {
            console.log('Finished in ' + event.elapsedTime + ' seconds.');
          };
    
          speechSynthesis.speak(msg);

          
   }

  

   $(document).ready(function(){
    const months = document.getElementsByClassName("month");
   for (let i = 0; i < months.length; i++) {
   
       $(months[i]).on('click',
           function()
       {
           /* console.log("sdsdsd "+$(this)); */
           /* $('#field-function_purpose').text() */
           readText($(this).text());
       });
   }

});
  