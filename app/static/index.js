function log_out(){$.get("/secret", function(){$("#logout").css("display", "block"), $("#login").css("display", "none");})}

window.addEventListener('load', (event) => {
    log_out();
});

$("#logout").click(function (){
    $.post("/auth/cookie/logout", function(response){setTimeout(() => { location.reload(); }, 500)})
})