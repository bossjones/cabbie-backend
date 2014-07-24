angular.module('cabbie-driver', ['ionic', 'ngResource', 'ngCookies', 'google-maps'])


// Constant & Configugration
// -------------------------

.constant('authRequired', true)
.constant('apiHost', 'http://localhost:8000')
.constant('locationHost', 'localhost:8080')

.config(['$httpProvider', function ($httpProvider) {
  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
  $httpProvider.interceptors.push('AuthInterceptor');
}])

.config([
    '$stateProvider', '$urlRouterProvider',
    function ($stateProvider, $urlRouterProvider) {
  $stateProvider
    .state('login', {
      url: '/login',
      templateUrl: 'templates/login.html',
      controller: 'LoginCtrl'
    })
    .state('signup', {
      url: '/signup',
      templateUrl: 'templates/signup.html',
      controller: 'SignupCtrl'
    })
    .state('app', {
      url: '/app',
      abstract: true,
      templateUrl: 'templates/menu.html',
      controller: 'AppCtrl'
    })
    .state('app.main', {
      url: '/main',
      views: {
        'menu-content' :{
          templateUrl: 'templates/main.html',
          controller: 'MainCtrl'
        }
      }
    });
  $urlRouterProvider.otherwise('/app/main');
}])


// Run
// ---

.run([
    '$rootScope', '$state', '$ionicPlatform', 'Auth', 'authRequired',
    function ($rootScope, $state, $ionicPlatform, Auth, authRequired) {
  $ionicPlatform.ready(function () {
    if (window.cordova && window.cordova.plugins.Keyboard) {
      cordova.plugins.Keyboard.hideKeyboardAccessoryBar(true);
    }
    if (window.StatusBar) {
      StatusBar.styleDefault();
    }
  });

  if (authRequired) {
    $rootScope.$on('$stateChangeStart', function (event, to, params){
      if (!Auth.isAuthenticated()) {
        if (['login', 'signup'].indexOf(to.name) == -1) {
          event.preventDefault();
          $state.go('login');
        }
      }
    });
  }
}])


// Factory
// -------

.factory('AuthInterceptor', [
    '$q', '$window', 'apiHost', function ($q, $window, apiHost) {
  return {
    request: function (config) {
      var token = $window.localStorage.getItem('auth.token');

      if (config.url.indexOf('/api') == 0) {
        config.url = apiHost + config.url;
      }

      config.headers = config.headers || {};
      if (!!token) {
        config.headers.Authorization = 'Token ' + token;
      }
      return config;
    },
    response: function (response) {
      if (response.status === 401) {
        // FIXME: Redirect to login state or seomthing
      }
      return response || $q.when(response);
    }
  };
}])
.factory('Auth', [
    '$q', '$http', '$window', '$rootScope',
    function ($q, $http, $window, $rootScope) {
  return {
    login: function (phone, password) {
      var deferred = $q.defer();

      $http.post('/api/auth/', { username: phone, password: password })
        .success(function (data) {
          $window.localStorage.setItem('auth.token', data.token);
          $rootScope.$broadcast('auth.login');
          deferred.resolve();
        })
        .error(function () {
          deferred.reject();
        });

      return deferred.promise;
    },
    logout: function () {
      angular.forEach(['auth.token'], function (key) {
        $window.localStorage.removeItem(key);
      });
      $rootScope.$broadcast('auth.logout');
    },
    getToken: function () {
      return $window.localStorage.getItem('auth.token');
    },
    isAuthenticated: function () {
      return !!$window.localStorage.getItem('auth.token');
    }
  };
}])
.factory('Passenger', ['$resource', function ($resource) {
  return $resource('/api/passengers/:id/:action', { id: '@id' }, {
    query: {
      method: 'GET',
      isArray: true,
      transformResponse: function (data) {
        return JSON.parse(data).results;
      }
    }
  });
}])
.factory('Driver', ['$resource', function ($resource) {
  return $resource('/api/drivers/:id/:action', { id: '@id' }, {
    query: {
      method: 'GET',
      isArray: true,
      transformResponse: function (data) {
        return JSON.parse(data).results;
      }
    }
  });
}])


// Controller
// ----------

.controller('AppCtrl', [
     '$scope', '$state', 'Auth', function ($scope, $state, Auth) {
  $scope.logout = function () {
    Auth.logout();
    $state.go('login');
  };
}])

.controller('LoginCtrl', [
    '$location', '$scope', '$ionicViewService', '$ionicPopup', '$ionicLoading',
    'Auth',
    function ($location, $scope, $ionicViewService, $ionicPopup, $ionicLoading,
              Auth) {
  $scope.data = {};
  $scope.submit = function () {
    $ionicLoading.show({ template: '<div class="spinner"></div>' });
    Auth.login($scope.data.phone, $scope.data.password)
      .then(function () {
        $location.url('/app/main');
      })
      .catch(function () {
        $ionicPopup.alert({
          title: '로그인 실패',
          template: '로그인 정보를 다시 확인해 주세요.',
          okText: '확인'
        });
      })
      .finally(function () {
        $ionicLoading.hide();
      });
  };

  var init = function () {
    var deregister = $scope.$on('$stateChangeStart', function () {
      $ionicViewService.nextViewOptions({
        disableAnimate: true,
        disableBack: true
      });
      deregister();
    });
  };

  init();
}])

.controller('SignupCtrl', [
    '$scope', '$location', '$ionicViewService', '$ionicLoading', '$ionicPopup',
    'Auth', 'Driver',
    function ($scope, $location, $ionicViewService, $ionicLoading, $ionicPopup,
              Auth, Driver) {
  $scope.data = {};
  $scope.submit = function () {
    var driver = new Driver($scope.data);
    $ionicLoading.show({ template: '<div class="spinner"></div>' });
    driver.$save().then(function () {
      Auth.login($scope.data.phone, $scope.data.password).then(function () {
        $ionicLoading.hide();
        $location.url('/app/main');
      });
    }, function (r) {
      var template = '<ul>';
      angular.forEach(r.data, function (value, key) {
        template += '<li>' + value + '</li>';
      });
      template += '</ul>';

      $ionicLoading.hide();

      $ionicPopup.alert({
        title: '가입 실패',
        template: template,
        okText: '확인'
      });
    });
  };

  var init = function () {
    var deregister = $scope.$on('$stateChangeStart', function () {
      $ionicViewService.nextViewOptions({
        disableAnimate: true,
        disableBack: true
      });
      deregister();
    });
  };

  init();
}])

.controller('MainCtrl', [
    '$scope', 'locationHost', 'Auth', function ($scope, locationHost, Auth) {
  $scope.located = false;
  $scope.map = {
    control: {},
    center: {
      latitude: 0,
      longitude: 0
    },
    zoom: 16
  };
  $scope.currentLocation = {};

  var onGetLocation = function () {
    var ws = new WebSocket('ws://' + locationHost + '/location');
    ws.onopen = function() {
      ws.send(JSON.stringify({
        token: Auth.getToken(),
        location: $scope.currentLocation
      }));
    };
    ws.onmessage = function (evt) {
      console.log(evt.data);
    };
  };
  var init = function () {
    navigator.geolocation.getCurrentPosition(function (position) {
      $scope.map.control.refresh(position.coords);
      $scope.currentLocation = position.coords;
      $scope.located = true;
      onGetLocation();
    });
  };

  init();
}]);

;
