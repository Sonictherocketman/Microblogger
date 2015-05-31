/**
 * Timeline actions
 */
 
 function retweet(el) {
 	el = $(el)
 	$.post(el.attr('href'), { 
 		username: el.attr('username'),
 		user_id: el.attr('user_id'),
 		user_link: el.attr('user_link'),
 		status_id: el.attr('status_id'),
 		status_pubdate: el.attr('status_pubdate')
 	}).done(function() { el.attr('disabled'); })
 	.error(function() { alert('failed') });
 }
 
 function block(el) {
 	el = $(el)
 	$.post(el.attr('href'), { 
 		username: el.attr('username'),
 		user_id: el.attr('user_id'),
 		user_link: el.attr('user_link')
 	}).done(function() { el.attr('disabled'); })
 	.error(function() { alert('failed') });  
 }
 
 function follow(el) {
 	el = $(el)
 	$.post(el.attr('href'), { 
 		username: el.attr('username'),
 		user_id: el.attr('user_id'),
 		user_link: el.attr('user_link')
 	}).done(function() { el.attr('disabled'); })
 	.error(function() { alert('failed') }); 
 }
 
 function del(el) {
 
 }
 
 
/*
 * Button/Link functions
 */

/**
 * Uses the timeline view below the toolbar and appends a new
 * blank post template object with input fields for the new post.
 */
function toggleNewPostTemplate() {
	var templateIsShown = document.getElementById('new-post-template-is-shown');
	if (templateIsShown.value !== 'true') {
		templateIsShown.value = 'true'
		var timeline = document.getElementById('post-list');
		var newPostTemplate = document.getElementById('new-post-template');
		timeline.innerHTML = newPostTemplate.innerHTML + timeline.innerHTML;	
	}
	else {
		//Remove the template from the view.
	}
}

/**
 * Uses the timeline view below the toolbar and appends a new
 * blank follow template object with input fields for the new follow.
 */
function toggleNewFollowTemplate() {
	var templateIsShown = document.getElementById('new-follow-template-is-shown');
	if (templateIsShown.value !== 'true') {
		templateIsShown.value = 'true'
		var timeline = document.getElementById('post-list');
		var newPostTemplate = document.getElementById('new-follow-template');
		timeline.innerHTML = newPostTemplate.innerHTML + timeline.innerHTML;	
	}
	else {
		//Remove the template from the view.
	}
}

/**
 * Displays a section that has the user's feed link for easy following.
 */
function toggleFollowMeMsg() {
	var templateIsShown = document.getElementById('follow-me-msg-is-shown');
	if (templateIsShown.value !== 'true') {
		templateIsShown.value = 'true'
		var timeline = document.getElementById('post-list');
		var newPostTemplate = document.getElementById('follow-me-msg');
		timeline.innerHTML = newPostTemplate.innerHTML + timeline.innerHTML;
		$('#follow-link')[0].focus();
	}
	else {
		//Remove the template from the view.
	}
}
