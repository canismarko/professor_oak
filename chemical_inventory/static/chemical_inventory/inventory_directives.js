angular.module('chemicalInventory')

// Interactive periodic table that allows user to select elements
    .directive('periodicTable', ['$http', '$resource', 'djangoUrl', function($http, $resource, djangoUrl) {
	// var elementsUrl = djangoUrl.reverse('')
	var elementsUrl = '/static/chemical_inventory/periodic_table.json';
	var templateUrl = '/static/chemical_inventory/periodic_table.html';
	var Chemical = $resource(djangoUrl.reverse('api:chemical-list'));
	function link(scope, elem, attr) {
	    scope.includedList = scope.$eval(scope.includedElements)
	    scope.excludedList = scope.$eval(scope.excludedElements)
	    // Retrieve list of elements from server
	    $http.get(elementsUrl).then(function(response) {
		var currentColumn, currentRow, element, elementIdx, newRow, isIncluded, isExcluded, state;
		scope.DEFAULT = 0;
		scope.INCLUDED = 1;
		scope.EXCLUDED = 2;
		scope.elementList = [];
		scope.allElements = [];
		// Determine how wide the table should be
		scope.totalWidth = $(elem).width();
		// Determine how many cells are in the periodic table
		scope.cellWidth = scope.totalWidth/18;
		// Prepare the rows by filling in missing boxes
		for (var rowIdx=0; rowIdx<response.data.table.length; rowIdx+=1) {
		    newRow = []
		    currentColumn = 0;
		    currentRow = response.data.table[rowIdx];
		    // For each element in the row, see if there's any skipped columns
		    for (elementIdx in currentRow.elements) {
			element = currentRow.elements[elementIdx];
			skippedBoxes = element.position - currentColumn;
			// Put in the necessary blank spaces
			while (currentColumn < element.position) {
			// for (var i=0; i<skippedBoxes; i++) {
			    newRow.push({
				display: false
			    });
			    currentColumn += 1;
			}
			// Determine if element should be selected
			isExcluded = (scope.excludedList.indexOf(element.small)>-1);
			isIncluded = (scope.includedList.indexOf(element.small)>-1);
			if (isExcluded) {
			    state = scope.EXCLUDED
			} else if (isIncluded) {
			    state = scope.INCLUDED
			} else {
			    state = scope.DEFAULT
			}
			// Push the actual element now
			var newElement = {
			    display: true,
			    state: state,
			    symbol: element.small,
			    number: element.number,
			    name: element.name,
			};
			newRow.push(newElement);
			scope.allElements.push(newElement);
			// Update the counter
			currentColumn = element.position + 1;
		    }
		    scope.elementList.push(newRow);
		}
	    });
	    // Handler for changing the state of each element
	    scope.cycleState = function(cell) {
		cell.state = (cell.state + 1) % 3
		// Remove the element from all lists
		function removeFromArray(array, cell) {
		    var idx = array.indexOf(cell.symbol);
		    if (idx !== -1) {
			array.splice(idx, 1);
		    }
		    return array;
		}
		removeFromArray(scope.includedList, cell);
		removeFromArray(scope.excludedList, cell);
		// Now add to the correct list
		if (cell.state == scope.INCLUDED) {
		    scope.includedList.push(cell.symbol);
		}
		if (cell.state == scope.EXCLUDED) {
		    scope.excludedList.push(cell.symbol);
		}
	    };
	    // Handler for submitting the query
	    scope.submitQuery = function() {
		// Redirect to same page with query parameters
		var path = window.location.pathname + "?";
		var includedList = scope.includedList;
		for (var i=0; i<includedList.length; i++) {
		    path += "required=" + includedList[i] + "&";
		}
		var excludedList = scope.excludedList
		for (var i=0; i<excludedList.length; i++) {
		    path += "excluded=" + excludedList[i] + "&";
		}
		 window.location.href = window.location.protocol + "//" + window.location.host + path;
	    };
	    // Helper for for setting all elements
	    scope.setAllElements = function(state) {
		// Reset element states
		for (var row=0; row<scope.elementList.length; row++) {
		    for (var idx=0; idx<scope.elementList[row].length; idx++) {
			element = scope.elementList[row][idx];
			element.state = state;
		    }
		}
	    };
	    scope.resetAll = function() {
		scope.excludedList = [];
		scope.includedList = [];
		scope.setAllElements(scope.DEFAULT);
	    };
	    scope.includeAll = function() {
		scope.excludedList = [];
		scope.includedList = scope.allElements.map(function(element) {
		    return element.symbol;
		});
		scope.setAllElements(scope.INCLUDED);
	    };
	    scope.excludeAll = function() {
		    scope.includedList = [];
		    scope.excludedList = scope.allElements.map(function(element) {
			return element.symbol;
		    });
		    scope.setAllElements(scope.EXCLUDED);
	    };
	}
	return {
	    templateUrl: templateUrl,
	    link: link,
	    transclude: true,
	    scope: {
		includedElements: '@',
		excludedElements: '@',
	    },
	}
    }])

// Specific element cell in the periodic table directive
    .directive('periodicTableElement', [function() {
	function link(scope, elem, attrs) {
	    var $elem = $(elem[0]);
	    var column = scope.cell.position;
	    // elem[0].style.left = column * scope.cellWidth + 'px';
	    // elem[0].style.height = scope.cellWidth + 'px';
	    // elem[0].style.left = column * 5.556 + '%';
	}
	return {
	    link: link
	};
    }])

// Directive for uploading files as part of a form
    .directive('fileModel', ['$parse', function($parse) {
	// https://uncorkedstudios.com/blog/multipartformdata-file-upload-with-angularjs
	return {
	    restrict: 'A',
	    link: function(scope, element, attrs) {
		var model = $parse(attrs.fileModel);
		var modelSetter = model.assign;

		element.bind('change', function() {
		    scope.$apply(function() {
			modelSetter(scope, element[0].files[0]);
		    });
		});
	    }
	};
    }])

    .directive('oakFormValidation', [function() {
    	function link(scope, elem, attrs) {
    	    // Add classes to labels of required fields
    	    $inputs = elem.find('input[ng-required],select[ng-required],textarea[ng-required]');
    	    for ( var i=0; i<$inputs.length; i++) {
    		$input = $($inputs[i]);
    		$label = $($input.prevAll('label')[0]);
    		$label.addClass('required');
    	    }
    	}
	return {
	    link: link
	};
    }])

    .directive('oakAddContainer', ['$filter', '$resource', 'djangoUrl', 'toaster', function($filter, $resource, djangoUrl, toaster) {
	function link(scope, elem, attrs) {
	    // Add classes to labels of required fields
	    $inputs = elem.find('input[ng-required],select[ng-required]');
	    for ( var i=0; i<$inputs.length; i++) {
		$input = $($inputs[i]);
		$label = $($input.prevAll('label')[0]);
		$label.addClass('required');
	    }
	    // Setup helper for adding new select options on the fly
	    function insertAddButton($select, $modal, Resource) {
		$select.wrap('<div class="row"><div class="col-md-10"></div></div>');
		var column = $select.parent();
		column.after('<div class="col-md-2"><button class="btn btn-default"><span class="glyphicon glyphicon-plus"></span> New</button></div>');
		var addButton = column.parent().find('button');
		addButton.bind('click', function() {
		    $modal.modal('show');
		});
		// Handler for button click -> show dialog for new glove
		scope.addThing
	    }
	    // Prepare for adding new glove on the fly
	    var gloveSelect = elem.find('select#id_gloves');
	    var gloveModal = elem.find('#glove-modal');
	    insertAddButton(gloveSelect, gloveModal);
	    var Glove = $resource(djangoUrl.reverse('api:glove-list'));
	    // Handler for submitting a new glove to the server
	    scope.addGlove = function(data) {
		Glove.save(scope.glove).$promise.then(function(newGlove) {
		    // Show user feedback for successfully saving new glove
		    gloveModal.modal('hide');
		    msg = 'Added ' + newGlove.name + " glove. It's super effective!";
		    toaster.success('Saved', msg);
		    // Add new glove to select input. TODO: Figure out how to select it
		    var option = '<option value="'+newGlove.id+'">';
		    option += newGlove.name;
		    option += '</option>';
		    gloveSelect.append(option);
		});
	    };
	    // Prepare for adding new supplier on the fly
	    var supplierSelect = elem.find('select#id_supplier');
	    var supplierModal = elem.find('#supplier-modal');
	    insertAddButton(supplierSelect, supplierModal);
	    // Handler for submitting new supplier to the server
	    var Supplier = $resource(djangoUrl.reverse('api:supplier-list'));
	    scope.addSupplier = function(data) {
		Supplier.save(scope.supplier).$promise.then(function(newSupplier) {
		    // Show user feedback for successfully saving new supplier
		    supplierModal.modal('hide');
		    msg = 'Added ' + newSupplier.name + ". It's super effective!";
		    toaster.success('Saved', msg);
		    // Add new supplier to select input. TODO: Figure out how to select it
		    var option = '<option value="'+newSupplier.id+'">';
		    option += newSupplier.name;
		    option += '</option>';
		    supplierSelect.append(option);
		});
	    };
	    // Check for an initial chemical passed in the url
	    var defaultChemicalId;
	    var regex = /chemical_id=([0-9]+)/i;
	    var match = regex.exec(window.location.search);
	    if (match) {
		defaultChemicalId = parseInt(match[1], 10);
	    } else {
		defaultChemicalId = 0;
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
			// "New chemical" is default
			scope.active_chemical_id = [defaultChemicalId];
		    }
		    // Update the id=0 dummy chemical
		    existing_chemicals[0].name = newName;
		    // Add filtered array to scope
		    scope.matching_chemicals = newArray;
		});
	    });
	    // Update the form fields when the user changes chemicals
	    scope.$watch('active_chemical_id', changeChemical);
	    function changeChemical(newId) {
		var newId = newId ? newId[0] : 0;
		// Retrieve the chemical object
		var newChemical = scope.existing_chemicals.filter(function(obj) {
		    return obj.id == newId;
		})[0];
		// Prepare model data
		if (newChemical) {
		    scope.chemical = newChemical;
		    // Fix some attributes so they match the select options
		    newChemical.health = newChemical.health.toString();
		    newChemical.flammability = newChemical.flammability.toString();
		    newChemical.instability = newChemical.instability.toString();
		    for (var i=0; i<newChemical.gloves.length; i++) {
			newChemical.gloves[i] = newChemical.gloves[i].toString();
		    }
		    // Disable the chemical entry if an existing chemical has been selected
		    inputs = elem.find('.chemical-form input,.chemical-form select');
		    if (newId > 0) {
			inputs.attr('disabled', 'disabled');
		    } else {
			inputs.removeAttr('disabled');
		    }
		}
	    } // end of function changeChemical
	}
	return {
	    link: link
	};

    }])

    .directive('oakNfpaDiamond', ['staticUrls', function(staticUrls) {
	function link(scope, elem, attrs) {
	    var SQRT_TWO = Math.sqrt(2);
	    // Color definitions
	    var blue = "#6691ff";
	    var red = "#ff6666";
	    var yellow = "#fcff66";
	    var white = "#ffffff";
	    // Size defaults (in pixels)
	    var height = 200;
	    var width = 200;
	    var borderWidth = 3;
	    // Object prototype for a box
	    function NfpaBox(color, diagonal, center) {
		this.color = color;
		this.diagonal = diagonal;
		this.center = center;
		// Find coordinates of rectangle
		vertices = {
		    left: {x: center.x - diagonal/2, y: center.y},
		    right: {x: center.x + diagonal/2, y: center.y},
		    top: {x: center.x, y: center.y - diagonal/2},
		    bottom: {x: center.x, y: center.y + diagonal/2},
		};
		this.draw = function(ctx) {
		    ctx.beginPath();
		    // Draw border
		    ctx.lineWidth = borderWidth;
		    ctx.moveTo(vertices.left.x, vertices.left.y);
		    ctx.lineTo(vertices.top.x, vertices.top.y);
		    ctx.lineTo(vertices.right.x, vertices.right.y);
		    ctx.lineTo(vertices.bottom.x, vertices.bottom.y);
		    ctx.lineTo(vertices.left.x, vertices.left.y);
		    ctx.stroke();
		    // Draw background
		    ctx.fillStyle = color;
		    ctx.fill();
		}
		this.setText = function(ctx, text) {
		    ctx.lineWidth = 1;
		    ctx.font = "40px sans-serif";
		    ctx.textAlign = "center";
		    ctx.fillStyle = "#000000";
		    ctx.fillText(text, center.x, center.y+15);
		}
	    }
	    // Get drawing context
	    var ctx = elem[0].getContext("2d");
	    ctx.canvas.width = width+borderWidth;
	    ctx.canvas.height = height+borderWidth;
	    // Define the four boxes
	    var diagonal = width/2-borderWidth * 3;
	    var healthBox = new NfpaBox(blue, diagonal,
					{x: width/4 + borderWidth,
					 y: height/2});
	    healthBox.draw(ctx);
	    healthBox.setText(ctx, scope.health);
	    var flammabilityBox = new NfpaBox(red, diagonal,
					      {x: width/2,
					       y: height/4 + borderWidth});
	    flammabilityBox.draw(ctx);
	    flammabilityBox.setText(ctx, scope.flammability);
	    var instabilityBox = new NfpaBox(yellow, diagonal,
					     {x: 3*width/4 - borderWidth,
					      y: height/2});
	    instabilityBox.draw(ctx);
	    instabilityBox.setText(ctx, scope.instability);
	    var specialBox = new NfpaBox(white, diagonal,
					 {x: width/2,
					  y: 3*height/4 - borderWidth});
	    specialBox.draw(ctx);
	    specialBox.setText(ctx, scope.specialHazards);
	}
	return {
	    link: link,
	    scope: {
		health: '@health',
		flammability: '@flammability',
		instability: '@instability',
		specialHazards: '@specialHazards',
	    },
	    templateUrl: staticUrls.nfpaDiamond,
	}
    }])
