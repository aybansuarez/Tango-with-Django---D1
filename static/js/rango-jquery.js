$(document).ready(function() {
  // JQuery code to be added in here.
  $('#about-btn').click(function(event){
    alert('You clicked the button using jQuery');
  });

  var path = window.location.pathname;
  if (path != '/rango/') {
    $("#navbarCollapse a[href*='"+path+"']").addClass("headeractive");
  } else {
    $('.home-rango').addClass('headeractive')
  }

  $("#about-btn").removeClass('btn-primary').addClass('btn-success');

  $('#about-btn').click(function (e) { 
    msgstr = $('#msg').html()
    msgstr = msgstr + "ooo"
    $("#msg").html(msgstr)
  });
  
}); 