$(document).ready(function () {
    $.get("/users/me", function(){$("#logout").css("display", "block"), $("#login").css("display", "none");})
})

$("#logout").click(function (){
    $.post("/auth/cookie/logout", function(response){setTimeout(() => { location.reload(); }, 100)})
})