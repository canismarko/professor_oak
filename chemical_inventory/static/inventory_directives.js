angular.module('chemicalInventory')

    .directive('poAddContainer', ['$filter', function($filter) {
	function link(scope, elem, attrs) {
	    // Add classes to labels of required fields
	    $inputs = elem.find('input[ng-required],select[ng-required]');
	    for ( var i=0; i<$inputs.length; i++) {
		$input = $($inputs[i]);
		$label = $($input.prevAll('label')[0]);
		$label.addClass('required');
	    }
	    // Search for a new chemical when a user types a name
	    scope.$watch('chemical_name', function(newName) {
		scope.existing_chemicals.$promise.then(function(existing_chemicals) {
		    var re, newArray;
		    // Add to new array only if regular expression matches
		    if (newName) {
			re = new RegExp(newName, 'i');
			newArray = $filter('filter')(existing_chemicals, function(chemical, idx, arr) {
			    return re.test(chemical.name) || chemical.id == 0;
			});
		    } else {
			// Chemical name is empty string
			newArray = existing_chemicals.slice();
		    }
		    // Select a default chemical on the new list
		    if (newArray.length > 1 && newName) {
			// First (real) chemical on list is default
			scope.active_chemical_id = [newArray[1].id];
		    } else {
			//     // "New chemical" is default
			scope.active_chemical_id = [0];
		    }
		    // Update the id=0 dummy chemical
		    existing_chemicals[0].name = newName;
		    // Add filtered array to scope
		    scope.matching_chemicals = newArray;
		});
	    });
	    // Update the form fields when the user changes chemicals
	    scope.$watch('active_chemical_id', function(newId) {
		newId = newId ? newId[0] : 0;
		// Retrieve the chemical object
		newChemical = scope.existing_chemicals.filter(function(obj) {
		    return obj.id == newId;
		})[0];
		// Prepare model data
		if (newChemical) {
		    scope.chemical = newChemical;
		    // Fix some attributes so they match the select options
		    newChemical.health = newChemical.health.toString();
		    newChemical.flammability = newChemical.flammability.toString();
		    newChemical.instability = newChemical.instability.toString();
		    newChemical.glove = newChemical.glove.toString();
		    // Disable the chemical entry if an existing chemical has been selected
		    inputs = elem.find('.chemical-form input,.chemical-form select');
		    if (newId > 0) {
			inputs.attr('disabled', 'disabled');
		    } else {
			inputs.removeAttr('disabled');
		    }
		}
	    });
	}
	return {
	    link: link
	};

    }])
