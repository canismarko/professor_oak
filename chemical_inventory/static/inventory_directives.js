angular.module('chemicalInventory')

    .directive('oakAddContainer', ['$filter', function($filter) {
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

    .directive('oakNfpaDiamond', [function() {
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
	    console.log(scope);
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
	}
    }])
