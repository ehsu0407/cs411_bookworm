/**
 * Created by Eddie on 4/23/2015.
 */

// Do search and update results
$("#submit-search").click(function(){
    button = $(this);
    var searchquery = $("#search-bar").val();

    // Disable the button while we add the item to cart
    this.disabled = "disabled";

    var postdata = {
        searchquery: searchquery,
        action: "get_media_search_results"
    };
    $.post('/media/', postdata, function(data){
        // On success
        var response = jQuery.parseJSON(data);

        if(response['status'] == 'too_short') {
            $("#search-error-message").html("Error, search query too short. At least three characters required.")
        } else {
            // Update the search results
            $("#search-results").html(response['search_results_html']);
        }


        // Revert the row back to normal
        button.removeAttr("disabled");
    });
});


// Do search and update results
$("#loan-submit-search").click(function(){
    button = $(this);
    var searchquery = $("#loan-search-bar").val();

    // Disable the button while we add the item to cart
    this.disabled = "disabled";

    var postdata = {
        searchquery: searchquery,
        action: "get_loan_search_results"
    };
    $.post('/loan/', postdata, function(data){
        // On success
        var response = jQuery.parseJSON(data);

        if(response['status'] == 'too_short') {
            $("#loan-search-error-message").html("Error, search query too short. At least three characters required.")
        } else {
            // Update the search results
            $("#loan-search-results").html(response['search_results_html']);
        }


        // Revert the row back to normal
        button.removeAttr("disabled");
    });
});


// Do search and update results for friends
$("#submit-search-friends").click(function(){
    button = $(this);
    var searchquery = $("#search-bar-friends").val();

    // Disable the button while we add the item to cart
    this.disabled = "disabled";

    var postdata = {
        searchquery: searchquery,
        action: "get_friend_search_results"
    };
    $.post('/profile/addfriend/', postdata, function(data){
        // On success
        var response = jQuery.parseJSON(data);

        // Update the search results
        $("#search-results-html").html(response['search_results_html']);

        // Revert the row back to normal
        button.removeAttr("disabled");
    });
});


// Add a book to library
$(document).delegate('.add-media-btn', 'click', function(){
    button = $(this);
    button.attr("disabled", "disabled");
    button.html("Adding")

    var media_id = button.val();

    var postdata = {
        media_id: media_id,
        action: "add_media_to_list"
    };

    $.post('/profile/mymedia/', postdata, function(data){
        // On success

        var response = jQuery.parseJSON(data);

        if(response['status'] == 'success'){
            // Mark the button as owned.
            button.html('Owned');
        }
        else
        {
            // Restore the button if failed
            button.html('Add To List');
            button.removeAttr("disabled");
        }

    });
});


// Add a isbn book to library
$(document).delegate('.add-media-btn-isbn', 'click', function(){
    button = $(this);
    button.attr("disabled", "disabled");
    button.html("Adding")

    var media_isbn = button.val();

    var postdata = {
        media_isbn: media_isbn,
        action: "add_media_to_list_isbn"
    };

    $.post('/profile/mymedia/', postdata, function(data){
        // On success

        var response = jQuery.parseJSON(data);

        if(response['status'] == 'success'){
            // Mark the button as owned.
            button.html('Owned');
        }
        else
        {
            // Restore the button if failed
            button.html('Add To List');
            button.removeAttr("disabled");
        }

    });
});


// Create new loan request
$(document).delegate('.loan-request-button', 'click', function(){
    button = $(this);
    var media_id = button.data('mediaid');

    var postdata = {
        unique_media_id: media_id,
        action: "send_loan_request"
    };

    $.post('/loan/', postdata, function(data){
        // On success

        var response = jQuery.parseJSON(data);

        // Mark the button as pending.
        btn_id = "#btn-loan-req-".concat(media_id)

        $(btn_id).html('Pending');
        $(btn_id).attr("disabled", "disabled");

    });
});


// Create new friend request
$(document).delegate('.add-friend-button', 'click', function(){
    button = $(this);
    var friend_id = button.val();
    btn_id = "#btn-add-friend-".concat(friend_id)

    // Disable the button to avoid double sending
    $(btn_id).attr("disabled", "disabled");

    var postdata = {
        friend_id: friend_id,
        action: "add_friend"
    };

    $.post('/profile/addfriend/', postdata, function(data){
        // On success

        var response = jQuery.parseJSON(data);

        // Mark the button as pending

        $(btn_id).html('Pending');
        $(btn_id).attr("disabled", "disabled");

    });
});

