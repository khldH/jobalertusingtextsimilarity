$(document).ready(function() {
    $('#overlay').hide();
    $('#overlay-login').hide();
    $("#all").change(function () {
        if ($(this).is(":checked")) {
                $(".job-description").prop("disabled", true).val("");
                 $(".job-description").css("background-color", "gray");
                }
        else {
                $(".job-description").prop("disabled", false)
                 $(".job-description").removeAttr("style");
            }
       });
    $('#subscribeForm').submit(function(event){
				event.preventDefault();
				// Show overlay spinner
				// Disable form elements
				$('#subscribeForm :input').prop('disabled', true);
				$('#overlay').fadeIn(300);

				// Get form data
				var formData = {
					email: $('#email').val(),
					job_description: $('#job_description').val(),
					is_all: $("#all").is(":checked"),
				};
				// Post form data to FastAPI endpoint
				$.ajax({
					url: '/subscribe',
					type: 'POST',
					data: JSON.stringify(formData),
					contentType: 'application/json',
					success: function(response){
					    $('#error-message').fadeOut();
						// Hide overlay spinner
						$('#overlay').fadeOut(function() {
                                // show the success message for a few seconds
                              $('#success-message').html('Successfully subscribed. Verification email has been sent to ' + formData.email + '. Please check your inbox and spam folder.');
                              $('#success-message').fadeIn(500).delay(5000).fadeOut()
                              // Enable form elements
						       $('#subscribeForm :input').prop('disabled', false);
                                // Clear form inputs
                                $('#subscribeForm')[0].reset();
                                $(".job-description").removeAttr("style");
                              });
                     },
					error: function(xhr, status, error){
					    // handle the error response
                        var errorResponse = JSON.parse(xhr.responseText);
                        console.log(errorResponse.error);
                        $('#error-message').text(errorResponse.error);
						// Hide overlay spinner
						$('#overlay').fadeOut();

						// Enable form elements
						$('#subscribeForm :input').prop('disabled', false);

						// Show error message
						$('#error-message').fadeIn();
					}
				});
			});
	$('#signupForm').submit(function(event){
				event.preventDefault();
				// Show overlay spinner
				// Disable form elements
				$('#signupForm :input').prop('disabled', true);
				$('#overlay').fadeIn(300);

				// Get form data
				var formData = {
					email: $('#email').val(),
					organization: $('#organization').val(),
					username: $("#username").val(),
				};
				// Post form data to FastAPI endpoint
				console.log(formData.email)
				$.ajax({
					url: '/create_organization',
					type: 'POST',
					data: JSON.stringify(formData),
					contentType: 'application/json',
					success: function(response){
					    $('#error-message').fadeOut();
						// Hide overlay spinner
						$('#overlay').fadeOut(function() {
                                // show the success message for a few seconds
                              $('#success-message').html('Account created successfully. Verification email has been sent to ' + formData.email + '. Please check your inbox and spam folder.');
                              $('#success-message').fadeIn(500).delay(5000).fadeOut()
                              // Enable form elements
						       $('#signupForm :input').prop('disabled', false);
                                // Clear form inputs
                                $('#signupForm')[0].reset();
                              });
                     },
					error: function(xhr, status, error){
					    // handle the error response
                        var errorResponse = JSON.parse(xhr.responseText);
                        console.log(errorResponse.error);
                        $('#error-message').text(errorResponse.error);
						// Hide overlay spinner
						$('#overlay').fadeOut();

						// Enable form elements
						$('#signupForm :input').prop('disabled', false);

						// Show error message
						$('#error-message').fadeIn();
					}
				});
			});
	$('#generateLoginLink').submit(function(event){
				event.preventDefault();
				// Show overlay spinner
				// Disable form elements
				$('#generateLoginLink :input').prop('disabled', true);
				$('#overlay-login').fadeIn(300);

				// Get form data
				var formData = {
					email: $('#account-email').val()
				};
				// Post form data to FastAPI endpoint
				console.log(formData.email)
				$.ajax({
					url: '/org/generate_login_link',
					type: 'POST',
					data: JSON.stringify(formData),
					contentType: 'application/json',
					success: function(response){
					    $('#error-message').fadeOut();
						// Hide overlay spinner
						$('#overlay-login').fadeOut(function() {
                                // show the success message for a few seconds
                              $('#success-message-login').html('If you have an active account, Login link has been sent to k ' + formData.email + '. Please check your inbox and spam folder.');
                              $('#success-message-login').fadeIn(500).delay(7000).fadeOut()
                              // Enable form elements
						       $('#generateLoginLink :input').prop('disabled', false);
                                // Clear form inputs
                                $('#generateLoginLink')[0].reset();
                                setTimeout(function() {
                                  $('#success-message-login').hide();
                                  $("#login-linkModal").modal("hide");
                                }, 5000);

                              });


                     },
					error: function(xhr, status, error){
					    // handle the error response
                        var errorResponse = JSON.parse(xhr.responseText);
                        console.log(errorResponse.error);
                        $('#error-message-login').text(errorResponse.error);
						// Hide overlay spinner
						$('#overlay-login').fadeOut();

						// Enable form elements
						$('#generateLoginLink :input').prop('disabled', false);

						// Show error message
						$('#error-message-login').fadeIn();
//						setTimeout(function() {
//                                  $('#error-message-login').hide();
//                                  $("#login-linkModal").modal("hide");
//                                }, 5000);
					}
				});
			});
	$('#createPost').submit(function(event){
				event.preventDefault();
				// Show overlay spinner
				// Disable form elements
				$('#createPost :input').prop('disabled', true);
				$('#overlay').fadeIn(300);
                tinyMCE.triggerSave();
				// Get form data
				var formData = {
				    title: $('#post-title').val(),
				    organization: $('#organization').val(),
				    type: $('#post-type').val(),
				    location: $('#location').val(),
					end_date: $('#end-date').val(),
					details:$('#post-details').val()
				};
				// Post form data to FastAPI endpoint
//				console.log(formData.post_details, formData.post_title)
				$.ajax({
					url: '/create_post',
					type: 'POST',
					data: JSON.stringify(formData),
					contentType: 'application/json',
					success: function(response){
					console.log(response)
					    $('#error-message').fadeOut();
						// Hide overlay spinner
						$('#overlay').fadeOut(function() {
                                // show the success message for a few seconds
                              $('#success-message').html('Post created successfully');
                              $('#success-message').fadeIn(500).delay(2000).fadeOut(function(){
                                var redirectUrl = response.url;
                                console.log(redirectUrl)
                                window.location.href = redirectUrl;
                              });

						       $('#createPost :input').prop('disabled', false);
                                // Clear form inputs
                                $('#createPost')[0].reset();
                              });
//                       setTimeout(function() {
//                              window.location.href = "/";
//                            }, 2000); // wait 5 seconds before redirecting
                     },
					error: function(xhr, status, error){
					    // handle the error response
					    console.log(xhr.responseText)
                        var errorResponse = JSON.parse(xhr.responseText);
                        console.log(errorResponse.error);
                        $('#error-message').text(errorResponse.error);
						// Hide overlay spinner
						$('#overlay').fadeOut();

						// Enable form elements
						$('#createPost :input').prop('disabled', false);

						// Show error message
						$('#error-message').fadeIn();
					}
				});
			});
			//

});
