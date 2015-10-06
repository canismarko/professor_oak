/**
 * Sets up the Keywords list page. Called on page ready.
 */
function keywords_list_init(){
  // Set the click event for the delete buttons.
  ....
 
  // Initialize the ability to select all rows from a checkbox in the data header row.
  ....
 
  // Set up the delete all selected button.
  ....
 
  // Set up pagination links click events.
  ....
 
  // Setup the keyword search filter.
  $('#search').bind('keydown', function(e) {
    if (e.keyCode == 13) {
      rebuild_keywords_list_args();
    }
  });
  $('#search-button').bind('click', function() {
    rebuild_keywords_list_args();
  });
 
  // Setup the number of results to show, domain filter, and sort options change events.
  $('#num-show, #domain, #sort').bind('change', function() {
    rebuild_keywords_list_args();
  });
 
  // Setup all of our glossary filters that are available as clickable. 
  $('#glossary li.avail').bind('click', function() {
    $('#glossary li').removeClass('active');
    $(this).addClass('active');
    rebuild_keywords_list_args();
  });
 
}
 
/**
 * Rebuild the list of filter and sort arguments and reload the page.
 */
function rebuild_keywords_list_args(export_flag) {
  var show = $('#num-show').val();
  var domain = $('#domain').val();
  var sort = $('#sort').val();
  var search = $('#search').val();
  var page = $('#page-num').val();
  var glossary = $('#glossary li.active').attr('data-id');
  if (!page) {
    page = 1;
  }
 
  var new_loc = window.location.pathname + '?page=' + page;
  if (show) {
    new_loc += '&show=' + show;
  }
  if (sort) {
    new_loc += '&sort=' + sort;
  }
  if (domain) {
    new_loc += '&domain=' + domain;
  }
  if (glossary) {
    new_loc += '&glossary=' + encodeURIComponent(glossary);
  }
  if (search) {
    new_loc += '&search=' + encodeURIComponent(search);
  }
  if (export_flag) {
    new_loc += '&export=1';
  }
 
  window.location.href = new_loc;
}