angular.module('chemicalInventory')
//angular.module('chemicalInventory', ['ngSanitize'])

// Let the user search using an interactive periodic table
    .controller('periodicTable', ['$scope', function($scope) {
	// Create some lists for which elements are checked
	$scope.includedList = [];
	$scope.excludedList = [];
    }])

    .controller('addContainer', ['$scope', '$resource', 'djangoUrl', 'toaster', 'Chemical', '$location', 'redirect', function($scope, $resource, djangoUrl, toaster, Chemical, $location, redirect) {
	// Get the list of currently existing chemicals the user can choose from
	$scope.existing_chemicals = Chemical.query();
	$scope.existing_chemicals.$promise.then(function(chemicalList) {
	    var chemical;
	    // Set an additional display attribute
	    for (var i=0; i < chemicalList.length; i++) {
		chemical = chemicalList[i];
		chemical.$displayName = chemical.name;
	    }
	    // Add a dummy entry for creating a new chemical
	    var dummyChemical = {
		id: 0,
		name: '[New chemical]',
		health: '',
		flammability: '',
		instability: '',
		special_hazards: '',
		gloves: [],
		$displayName: '[New chemical]',
	    };
	    chemicalList.splice(0, 0, dummyChemical);
	});
	// Automatically set default for opened and expiration dates
	var today = new Date();
	// var date_opened = today.toISOString().split('T')[0];
	var expiration_date = new Date();
	expiration_date.setFullYear(1+expiration_date.getFullYear());
	// Helper function resets the container form to an empty pristine state
	function resetContainer() {
	    $scope.container = {
		date_opened: today,
		expiration_date: expiration_date,
		quantity: 100,
		unit_of_measure: 'g',
	    };
	    if (typeof $scope.container_form != 'undefined' ) {
		$scope.container_form.$setPristine();
	    }
	}
	resetContainer();
	// Handler for error feedback
	function showError(reason) {
	    // Display visual feedback of error
	    var message = "Chemical not added. Please contact your administrator";
	    toaster.pop({
		type: 'error',
		title: 'Error!',
		body: message,
		timeout: 0,
		showCloseButton: true
	    });
	}
	// Save the entered form data
	function save_container(container, options) {
	    var Container = $resource(djangoUrl.reverse('api:container-list'));
	    // Determine if a label should be printed
	    if (options && options.printLabel) {
		container.$print_label = true;
	    } else {
	    	container.$print_label = false;
	    }
	    var newContainer = Container.save(container);
	    var promise = newContainer.$promise;
	    promise.then(function(container) {
		// Get URL of chemical and redirect
		var successUrl = djangoUrl.reverse('chemical_detail',
						   {pk: container.chemical});
		redirect(successUrl);
	    }, showError);
	    return promise
	}
	$scope.save = function(options) {
	    // Check if a new chemical is being saved
	    if ($scope.chemical.id > 0) {
		// Existing chemical -> save container directly
		$scope.container.chemical = $scope.chemical.id;
		save_container($scope.container, options);
	    } else {
		// New chemical -> send the new chemical to the server first
		Chemical.save($scope.chemical)
		    .then(function(responseChemical) {
			// On completion, save the container
			$scope.container.chemical = responseChemical.data.id;
			save_container($scope.container, options);
		    }, showError);
	    }
	};
    }])

// Controller handles the list of containers for a given chemical,
// eg. allowing the user to set the .is_empty attribute via a checkbox
    .controller('chemicalList', ['$scope', '$resource', '$http', 'djangoUrl', function($scope, $resource, $http, djangoUrl) {
	// Handler for changing empty status
	$scope.updateStatus = function() {
	    var containerUrl, Container, container;
	    // Get the container object from the API
	    containerUrl = djangoUrl.reverse('api:container-detail',
					     {pk: $scope.chemicalId});
	    var payload = {is_empty: $scope.isEmpty};
	    $http.patch(containerUrl, {is_empty: $scope.isEmpty});
	};
    }])

    // Controller to print a label to the pi
    .controller('printButton',['$scope','djangoUrl', '$http', 'toaster', function($scope, djangoUrl, $http, toaster){
        $scope.sendPrintJob=function(containerpk) {
            printUrl = djangoUrl.reverse('print_label',{container_pk: containerpk});
            $http.get(printUrl).then(function(response) {
                toaster.pop({
                type: 'success',
                title: 'Success!',
                body: "Your label has been printed in 4163 SES",
                timeout: 0,
                showCloseButton: true
                });
            }, function(response) {
                toaster.pop({
                type: 'error',
                title: 'Error!',
                body: "An error occured while printing your label. Please contact the site administrator",
                timeout: 0,
                showCloseButton: true
                });
        })};
    }])

    // Controller to quick_empty a container from the pk
    .controller('quickEmpty',['$scope','djangoUrl', '$http', 'toaster', '$resource', 'Chemical', 'currentUser', function($scope, djangoUrl, $http, toaster, $resource, Chemical, currentUser){
        $scope.submit=function() {
            quickEmptyUrl = djangoUrl.reverse('api:container-detail',{pk: $scope.containerpk});
            // $http.get(quickEmptyUrl, {is_empty:true}).then(function(response) {
                // if (response.is_empty == true) {
                    // toaster.pop({
                    // type: 'success',
                    // title: 'Success!',
                    // body: "Container number " + $scope.containerpk + " is already marked as empty!",
                    // timeout: 0,
                    // showCloseButton: true
                    // });
                // console.log(quickEmptyUrl);
            // } else {
                $http.patch(quickEmptyUrl, {is_empty:true, emptied_by:currentUser.pk}).then(function(response) {
                    toaster.pop({
                    type: 'success',
                    title: 'Success!',
                    body: "Container number " + $scope.containerpk + " has been marked as empty",
                    timeout: 0,
                    showCloseButton: true
                    });
                console.log(quickEmptyUrl);
                $scope.containerpk = "";
                }, function(response)
                 {
                    if (response.status == '500') {
                        var message = "Please enter the containers barcode number in order to mark it as empty"
                    } else if (response.status == '404') {
                        var message = "Container " + $scope.containerpk + " cannot be found. Are you sure you entered it correctly?"
                    } else {
                        var message = "Unknown error, contact the site administrator"
                    }
                    toaster.pop({
                    type: 'error',
                    title: 'Error!',
                    body: message,
                    timeout: 0,
                    showCloseButton: true
                    });
                console.log(quickEmptyUrl);
                $scope.containerpk = "";
            })};
    }])

    // Controller to find a container from its pk number -- redirects to the chemical page with the container highlighted
    .controller('quickFind',['$scope','djangoUrl', '$http', '$window', 'toaster', '$resource', 'Chemical', 'currentUser', function($scope, djangoUrl, $http, $window, toaster, $resource, Chemical, currentUser){
        $scope.submit=function() {
            quickFindUrl = djangoUrl.reverse('api:container-detail',{pk: $scope.containerpk});
                $http.get(quickFindUrl).then(function(response) {
                    containerNumber = response.data.chemical;
                    $window.location.assign("/chemical_inventory/chemicals/" + containerNumber + '?find=' + $scope.containerpk);
                console.log(quickEmptyUrl);
                $scope.containerpk = "";
                }, function(response)
                 {
                    if (response.status == '500') {
                        var message = "Please enter the containers barcode number in order to search for it"
                    } else if (response.status == '404') {
                        var message = "Container " + $scope.containerpk + " cannot be found. Are you sure you entered it correctly?"
                    } else {
                        var message = "Unknown error, contact the site administrator"
                    }
                    toaster.pop({
                    type: 'error',
                    title: 'Error!',
                    body: message,
                    timeout: 0,
                    showCloseButton: true
                    });
                console.log(quickFindUrl);
                $scope.containerpk = "";
            })};
    }])
    
// Let the user send an email using the oak_utilities/views.py command send_results_email()
	.controller('sendresultsEmail', ['$scope', 'djangoUrl', '$http', 'toaster', function($scope, djangoUrl, $http, toaster){
		$scope.sendEmailRequest=function(stockid) {
				requestUrl = djangoUrl.reverse('send_stock_email',{stock: stockid}
);
				$http.get(requestUrl).then(function(response) {
					toaster.pop({
					type: 'success',
					title: 'Email Sent!',
					body: "Continue discussion with your colleagues using 'Reply All' in your email client",
					timeuot: 0,
					showCloseButton: true
					});
				}, function(response) {
					toaster.pop({
					type: 'error',
					title: 'Error!',
					body: "An error occured while sending your email. Please contact the site administrator",
					timeout: 0,
					showCloseButton: true
					});
			})};
	}])


//Adding characters to a specific point where cursor is in specified element. if cursor in null (element hasn't yet been clicked) then nothing happens 
	.controller("AddWords", function($scope) {

	  $scope.lastFocused;
	  angular.element("input[id='id_formula']").focus(function() {
		$scope.lastFocused = document.activeElement;
	  });

	  //http://stackoverflow.com/questions/1064089/inserting-a-text-where-cursor-is-using-javascript-jquery
	  $scope.insertText = function(text) {
		var input = $scope.lastFocused;
		console.log(input);
		if (input == undefined) { return; }
		var scrollPos = input.scrollTop;
		var pos = 0;
		var browser = ((input.selectionStart || input.selectionStart == "0") ? 
			           "ff" : (document.selection ? "ie" : false ) );
		if (browser == "ie") { 
		  input.focus();
		  var range = document.selection.createRange();
		  range.moveStart ("character", -input.value.length);
		  pos = range.text.length;
		}
		else if (browser == "ff") { pos = input.selectionStart };

		var front = (input.value).substring(0, pos);  
		var back = (input.value).substring(pos, input.value.length); 
		input.value = front+text+back;
		pos = pos + text.length;
		if (browser == "ie") { 
		  input.focus();
		  var range = document.selection.createRange();
		  range.moveStart ("character", -input.value.length);
		  range.moveStart ("character", pos);
		  range.moveEnd ("character", 0);
		  range.select();
		}
		else if (browser == "ff") {
		  input.selectionStart = pos;
		  input.selectionEnd = pos;
		  input.focus();
		}
		input.scrollTop = scrollPos;
		console.log(angular.element(input).val());
		angular.element(input).trigger('input');
	  }

	})


// Provides a preview of the custom markdown in the formula field
	.controller('formulaPreview', ['$scope', '$sce', function($scope, $sce) {
		$scope.preview = "This is a <sup>test</sup> |H_2O";
		$scope.sanitizedPreview = function(input) {
			return $sce.trustAsHtml(input
				.replace(/<[^>]+>/gm, '')				//Removes any pre-existing tags
				.replace(/\|/g, "&bull;")				//replacing for hydrate
				.replace(/_(.){1}/g, "<sub>$1</sub>")	//replacing for subscript
				.replace(/\^(.)/g, "<sup>$1</sup>")		//replacing for superscript
			)
			};
	}])
