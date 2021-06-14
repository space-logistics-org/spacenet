var accesstoken="";

$("#login_form_submit").click(function (){
	/*$.ajax({
		url:"token",
		data:JSON.stringify({
			username:$("#username_field").val(),
			password:$("#password_field").val()
		}),
		contentType:"application/json",
		dataType:"json",
		method:"post",
		success:function (response){
			alert(response)
		}
	})*/
	$.post("token", $("#login").serialize(), function (response){accesstoken=response["access_token"]})
})

$("#get_current_user").click(function (){
	$.ajax({url:"users/me", success:function(response){console.log(response)}, headers:{Authorization:"Bearer "+accesstoken}})
})