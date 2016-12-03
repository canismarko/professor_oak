angular.module('chemicalInventory')

    .filter('chunk', [function() {
	// Filter that breaks an array up into smaller sub-arrays of given size
	function chunk(arr, size) {
	    var newArr = [];
	    for (var i=0; i<arr.length; i+=size) {
		newArr.push(arr.slice(i, i+size));
	    }
	    return newArr;
	}
	return chunk
    }])
