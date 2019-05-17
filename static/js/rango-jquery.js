$(document).ready(function() {
  // JQuery code to be added in here.
  $('#about-btn').click(function(event){
    alert('You clicked the button using jQuery');
  });
  $("#about-btn").removeClass('btn-primary').addClass('btn-success');
}); 