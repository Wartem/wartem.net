(function(){
  function closeMenus(exceptMenu){
    document.querySelectorAll(".recovery-collection-menu[open]").forEach(function(menu){
      if(menu !== exceptMenu){
        menu.removeAttribute("open");
      }
    });
  }
  document.addEventListener("click", function(event){
    var menu = event.target.closest(".recovery-collection-menu");
    if(menu){
      closeMenus(menu);
      return;
    }
    closeMenus(null);
  });
  document.addEventListener("keydown", function(event){
    if(event.key === "Escape"){
      closeMenus(null);
    }
  });
  document.querySelectorAll(".recovery-collection-menu summary").forEach(function(summary){
    summary.addEventListener("click", function(){
      var menu = summary.closest(".recovery-collection-menu");
      if(!menu){
        return;
      }
      setTimeout(function(){
        if(menu.hasAttribute("open")){
          closeMenus(menu);
        }
      }, 0);
    });
  });
})();
