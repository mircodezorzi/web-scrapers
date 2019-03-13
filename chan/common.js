$(document).ready(function(){
    $(".image").click(function(){
        $(this).toggleClass("full");
    })

    $(".image").on('click', function(e) {
        if( e.which == 1 ) {
            e.preventDefault();
        }
    })
});
