describe('chemical inventory', function() {

    var $httpBackend, djangoUrl, $rootScope, $provide;
    beforeEach(module('chemicalInventory'));
    beforeEach(function() {
	// Mock the redirection mechanism
	module(function($provide) {
	    $provide.value('redirect', function(url) {
		console.log('redirect to '+url);
	    });
	});
    })

    beforeEach(inject(function($injector) {
	$rootScope = $injector.get('$rootScope');
	// Set mock endpoints
	djangoUrl = $injector.get('djangoUrl');
	$httpBackend = $injector.get('$httpBackend');
	$httpBackend.when('GET', djangoUrl.reverse('api:chemical-list')).
	    respond([]);
    }));

    afterEach(function() {
	// Check that all the requests fired properly
	$httpBackend.verifyNoOutstandingExpectation();
	$httpBackend.verifyNoOutstandingRequest();
    });

    describe('Chemical model service', function() {
	var Chemical
	beforeEach(inject(function($injector) {
	    Chemical = $injector.get('Chemical');
	}));
    	it('serializes manytomany fields', function() {
	    // Check that the resutling formdata has m2m fields separated
	    $httpBackend.expectPOST(
		djangoUrl.reverse('api:chemical-list'),
		function(postData) {
		    expect(postData.getAll('ghs_hazards')).toEqual(['2', '3'])
		    expect(postData.get('gloves')).toEqual('0')
		    return true
		}
	    ).respond(200);
	    // Save some data that have mutiple many to many field selections
	    var requestData = {
		name: 'Francium',
		ghs_hazards: [2, 3],
		gloves: [0, 1],
	    };
	    Chemical.save(requestData);
	    // Check that it still works fine with zero or 1 options selected
	    $httpBackend.expectPOST(
		djangoUrl.reverse('api:chemical-list'),
		function(postData) {
		    expect(postData.getAll('ghs_hazards')).toEqual(['0'])
		    expect(postData.get('gloves')).toEqual(null)
		    return true
		}
	    ).respond(200);
	    // Save some data that have mutiple many to many field selections
	    var requestData = {
		name: 'Francium',
		ghs_hazards: [0],
		gloves: [],
	    };
	    Chemical.save(requestData);
	    $httpBackend.flush();
    	});
    });

    describe('add container form', function() {
	var createController;
	beforeEach(inject(function($injector) {
	    // The $controller service is used to create instances of controllers
	    var $controller = $injector.get('$controller');
	    createController = function() {
		return $controller('addContainer', {'$scope' : $rootScope });
	    };
	}));
	it('posts the container when submitted', function() {
	    $httpBackend.expectPOST(
		djangoUrl.reverse('api:container-list'),
		function(data) {
		    // $print_label should be truthy
		    data = JSON.parse(data);
		    return !data.$print_label;
		}).
		respond({});
	    var controller = createController();
	    // Testing data for the model
	    $rootScope.chemical = {
		id: 1
	    };
	    $rootScope.save();
	    $httpBackend.flush();
	    expect(1).toEqual(1);
	});
	it('prints a new label', function() {
	    // Expected post behavior
	    $httpBackend.expectPOST(
	    	djangoUrl.reverse('api:container-list'),
	    	function(data) {
	    	    // $print_label should be truthy
	    	    data = JSON.parse(data);
	    	    return data.$print_label;
	    	}
	    ).respond({});
	    var controller = createController();
	    // Testing data for the model
	    $rootScope.chemical = {
		id: 1
	    };
	    $rootScope.save({printLabel: true});
	    $httpBackend.flush();
	    $httpBackend.expectPOST(
	    	djangoUrl.reverse('api:container-list'),
	    	function(data) {
	    	    // $print_label should be falsy (no options passed to save())
	    	    data = JSON.parse(data);
	    	    return !data.$print_label;
	    	}
	    ).respond({});
	    $rootScope.save()
	    $httpBackend.flush();
	    expect(1).toEqual(1);
	});
    });
});
