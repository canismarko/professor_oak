angular.module('chemicalInventory', ['ngResource', 'ngAnimate', 'toaster', 'ng.django.forms', 'ng.django.urls'])

// Set HTML5 mode for urls
    .config(function($locationProvider){
	// $locationProvider.html5Mode({
	//     enabled: true,
	//     requireBase: false,
	// });
    })

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
