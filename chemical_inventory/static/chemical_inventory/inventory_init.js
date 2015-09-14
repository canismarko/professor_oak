angular.module('chemicalInventory', ['ngResource', 'ngAnimate', 'toaster', 'ng.django.urls'])

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
