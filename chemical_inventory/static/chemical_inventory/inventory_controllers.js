angular.module('chemicalInventory')

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
            })
        }
    }])
