angular.module('chemicalInventory', ['ngResource'])

// Set csrf token and AJAX header
    .config(function($httpProvider) {
	$httpProvider.defaults.xsrfCookieName = 'csrftoken';
	$httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
	$httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    })

// Retain trailing slash on urls
    .config(function($resourceProvider) {
	$resourceProvider.defaults.stripTrailingSlashes = false;
    })

    .controller('addContainer', ['$scope', '$resource', function($scope, $resource) {
	var Chemical;
	// Get the list of currently existing chemicals the user can choose from
	Chemical = $resource('/chemical_inventory/api/chemicals/');
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
		glove: '',
		$displayName: '[New chemical]',
	    };
	    chemicalList.splice(0, 0, dummyChemical);
	});
	// Automatically set default for opened and expiration dates
	var today = new Date();
	var date_opened = today.toISOString().split('T')[0];
	var expiration_date = new Date();
	expiration_date.setFullYear(1+expiration_date.getFullYear());
	expiration_date = expiration_date.toISOString().split('T')[0];
	$scope.container = {
	    date_opened: date_opened,
	    expiration_date: expiration_date,
	};
	// Save the entered form data
	function save_container(container) {
	    var Container = $resource('/chemical_inventory/api/containers/')
	    Container.save(container);
	}
	$scope.save = function() {
	    // Check if a new chemical is being saved
	    if ($scope.chemical.id > 0) {
		// Existing chemical -> save container directly
		$scope.container.chemical = $scope.chemical.id;
		save_container($scope.container);
	    } else {
		// New chemical -> send the new chemical to the server first
		var newChemical = Chemical.save($scope.chemical);
		newChemical.$promise.then(function(chemical) {
		    // On completion, save the container
		    $scope.container.chemical = chemical.id;
		    save_container($scope.container);
		});
	    }
	};
    }])
