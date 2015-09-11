angular.module('chemicalInventory', ['ngResource'])

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
    }])
