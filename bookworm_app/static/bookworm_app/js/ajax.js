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

