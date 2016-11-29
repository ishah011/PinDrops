$(document).on('change', '.div-toggle', function() {
  var target = $(this).data('target');
  var show = $("option:selected", this).data('show');
  $(target).children().addClass('hide');
  $(show).removeClass('hide');
});
$(document).ready(function(){
	$('.div-toggle').trigger('change');
});

function admissions() {
    document.getElementById('admissions').style.display='block';
}
function revenue() {
	document.getElementById('revenue').style.display='block';
}
function budget() {
    document.getElementById('budget').style.display='block';
}
function genres() {
	document.getElementById('genres').style.display='block';
}