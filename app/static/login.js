
var accesstoken="";

$("#login_form_submit").click(function (){
	/*
	$.ajax({
		url:"/auth/cookie/login",
		data:JSON.stringify({
			username:$("#username").val(),
			password:$("#password").val()
		}),
		contentType:"application/json",
		dataType:"json",
		method:"post",
		success:function (response){
			alert(response)
		}
	})*/

	
	$.post("/auth/cookie/login", $("#login").serialize(), function(){setTimeout(() => { history.back(); }, 500)})
	/*
	setTimeout(() => { $("#invalid").css("display", "block"); }, 500);
	function (response){accesstoken=response["access_token"]}*/

})

/*
$("#get_current_user").click(function (){
	$.ajax({url:"users/me", success:function(response){console.log(response)}, headers:{Authorization:"Bearer "+accesstoken}})
})
*/