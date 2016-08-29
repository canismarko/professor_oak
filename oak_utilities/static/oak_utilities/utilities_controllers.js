angular.module('oakUtilities', ['ngResource', 'ngAnimate', 'toaster', 'ng.django.forms', 'ng.django.urls'])

// Let the user send an email using the oak_utilities/views.py command send_results_email()
	.controller('sendresultsEmail', ['$scope', 'djangoUrl', '$http', 'toaster', function($scope, djangoUrl, $http, toaster){
		$scope.sendEmailRequest=function(stockid) {
				requestUrl = djangoUrl.reverse('send_stock_email',{stock_id: stockid}
);
				$https.get(requestUrl).then(function(response) {
					toaster.pop({
					type: 'success',
					title: 'Email Sent!',
					body: "Continue discussion with your colleagues using 'Reply All' in your email client",
					timeuot: 3,
					showCloseButton: true
					});
				}, function(response) {
					toaster.pop({
					type: 'error',
					title: 'Error!',
					body: "An error occured while sending your email. Please contact the site administrator",
					timeout: 0,
					showCloseButton: true
					});
			})};
	}])
