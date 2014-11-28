/**
 *
 */
 
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