angular.module('cabbie-driver', ['ionic', 'ngResource', 'ngCookies', 'google-maps'])


// Constant & Configugration
// -------------------------

.constant('apiHost', 'http://localhost:8000')
.constant('locationHost', 'localhost:8080')
.constant('authRequired', true)
.constant('locationTrackInterval', 1000)

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


// Filter
// ------

.filter('range', function() {
  return function(input, range) {
    start = range[0];
    end = range[1];
    offset = end > start ? 1 : -1;
    for (var i = start; i != end; i += offset) {
      input.push(i);
    }
    return input;
  };
})


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
.factory('RateModal', [
    '$q', '$rootScope', '$ionicModal', function ($q, $rootScope, $ionicModal) {
  return {
    open: function () {
      var deferred = $q.defer();
      var $scope = $rootScope.$new();

      $scope.modal = null;
      $scope.resolveData = null;
      $scope.model = {};

      $scope.$on('$destroy', function () {});
      $scope.$on('modal.removed', function () {});
      $scope.$on('modal.hidden', function () {
        $scope.resolveData && deferred.resolve($scope.resolveData);
      });

      $scope.close = function () {
        $scope.modal.remove();
      };
      $scope.submit = function () {
        $scope.resolveData = $scope.model;
        $scope.close();
      };
      $scope.init = function () {};

      $ionicModal.fromTemplateUrl('templates/rate-modal.html', {
        scope: $scope,
        animation: 'slide-in-up'
      }).then(function (instance) {
        $scope.modal = instance;
        $scope.modal.show();
        $scope.init();
      });

      return deferred.promise;
    }
  };
}])
.factory('Session', [
    '$q', '$timeout', '$ionicPopup', 'locationHost', 'locationTrackInterval', 'Auth', 'RateModal',
    function ($q, $timeout, $ionicPopup, locationHost, locationTrackInterval, Auth, RateModal) {
  var authenticated = false;
  var activated = false;
  var location = null;
  var state = null;
  var ws = null;
  var authCallbacks = [];
  var locationCallbacks = [];
  var stateCallbacks = [];

  var send = function (type, data) {
    ws.send(JSON.stringify({
      type: type,
      data: data
    }));
  };
  var track = function () {
    navigator.geolocation.getCurrentPosition(function (position) {
      location = {
        longitude: position.coords.longitude,
        latitude: position.coords.latitude
      };

      // FIXME
      location.longitude += (Math.random() - 1) * 5 / 1000.0;
      location.latitude += (Math.random() - 1) * 5 / 1000.0;

      (state == 'initialized' && activated || state == 'approved') && send('driver_update_location', {
        location: [location.longitude, location.latitude]
      });
      angular.forEach(locationCallbacks, function (callback) {
        callback(location);
      });
      $timeout(track, locationTrackInterval);
    });
  };
  var transitTo = function (newState, data) {
    var oldState = state;
    state = newState;
    angular.forEach(stateCallbacks, function (callback) {
      callback(newState, oldState, data);
    });
  };
  var onOpen = function () {
    send('auth', {
      role: 'driver',
      token: Auth.getToken()
    });
  };
  var onReceive = function (packet) {
    var payload = JSON.parse(packet.data);
    var data = payload.data;

    console.log(payload);

    switch (payload.type) {
      case 'error':
        alert(data.msg);
        break;

      case 'auth_succeeded':
        authenticated = true;
        angular.forEach(authCallbacks, function (callback) {
          callback();
        });
        transitTo('initialized');
        break;

      case 'driver_requested':
        transitTo('requested', data);
        break;

      case 'driver_canceled':
        $ionicPopup.alert({
          title: '콜 취소',
          template: '승객에 의해 콜이 취소되었습니다.',
          okText: '확인'
        });
        transitTo('initialized');
        break;

      case 'driver_disconnected':
        $ionicPopup.alert({
          title: '연결 끊김',
          template: '승객의 연결이 끊겼습니다.',
          okText: '확인'
        });
        transitTo('initialized');
        break;
    }
  };

  return {
    initialize: function () {
      if (!!ws) {
        return;
      }
      ws = new WebSocket('ws://' + locationHost + '/location');
      ws.onopen = onOpen;
      ws.onmessage = onReceive;

      track();
    },
    activate: function () {
      activated = true;
    },
    deactivate: function () {
      activated = false;
      send('driver_deactivate');
    },
    approve: function () {
      send('driver_approve');
      transitTo('approved');
    },
    reject: function (reason) {
      send('driver_reject', {
        reason: reason
      });
      transitTo('initialized');
    },
    arrive: function () {
      send('driver_arrive');
      transitTo('arrived');
    },
    board: function () {
      send('driver_board');
      transitTo('boarded');
    },
    complete: function () {
      var that = this;

      send('driver_complete');

      RateModal.open().then(function (data) {
        that.rate(data.rating, data.comment || '');
        transitTo('initialized');
      });
    },
    rate: function (rating, comment) {
      send('driver_rate', {
        rating: rating,
        comment: comment
      });
    },

    onLocationChange: function (callback) {
      locationCallbacks.push(callback);
    },
    onStateChange: function (callback) {
      stateCallbacks.push(callback);
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
    '$scope', '$ionicModal', 'locationHost', 'Session',
    function ($scope, $ionicModal, locationHost, Session) {
  $scope.located = false;
  $scope.activated = false;
  $scope.map = {
    control: {},
    center: {
      latitude: 0,
      longitude: 0
    },
    zoom: 15
  };
  $scope.location = {};
  $scope.state = null;
  $scope.modal = null;
  $scope.requestData = null;

  $scope.toggleActivate = function () {
    $scope.activated = !$scope.activated;
    Session[$scope.activated ? 'activate' : 'deactivate']();
  };
  $scope.showRequestModal = function () {
    if ($scope.processing) {
      return;
    }
    $scope.processing = true;

    $ionicModal.fromTemplateUrl('templates/request-modal.html', {
      scope: $scope,
      animation: 'slide-in-up'
    }).then(function (modal) {
      $scope.modal = modal;
      $scope.modal.show();
      $scope.processing = false;
    });
  };
  $scope.modalClose = function () {
    $scope.modal && $scope.modal.remove();
  };
  $scope.modalApprove = function () {
    $scope.modalClose();
    Session.approve();
  };
  $scope.modalReject = function () {
    var reason = 'test reason'; // FIXME: Needs to be explicitly selected
    $scope.modalClose();
    Session.reject(reason);
  };

  $scope.arrive = function () {
    Session.arrive();
  };
  $scope.board = function () {
    Session.board();
  };
  $scope.complete = function () {
    Session.complete();
  };

  var init = function () {
    Session.onLocationChange(function (location) {
      $scope.location = location;
      $scope.map.control.refresh(location);
      $scope.located = true;
    });
    Session.onStateChange(function (newState, oldState, data) {
      $scope.state = newState;

      switch (newState) {
        case 'requested':
          $scope.requestData = data;
          break;
      };
    });
    Session.initialize();
  };

  init();
}]);

;
