angular.module('cabbie-passenger', ['ionic', 'ngResource', 'ngCookies', 'google-maps'])


// Constant & Configugration
// -------------------------

.constant('authRequired', true)
.constant('apiHost', 'http://localhost:8000')
.constant('locationHost', 'localhost:8080')
//.constant('apiHost', 'http://bktaxi.com')
//.constant('locationHost', 'bktaxi.com:8080')
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


// Fitler
// ------

.filter('coord', function () {
  return function (val) {
    return {
      longitude: val[0],
      latitude: val[1]
    };
  };
})
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
  var location = null;
  var state = null;
  var chargeType = null;
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
      role: 'passenger',
      token: Auth.getToken()
    });
  };
  var onReceive = function (packet) {
    var payload = JSON.parse(packet.data);
    var data = payload.data;

    console.log(payload);

    switch (payload.type) {
      case 'error':
        $ionicPopup.alert({
          title: '오류',
          template: data.msg,
          okText: '확인'
        });
        break;

      case 'auth_succeeded':
        authenticated = true;
        angular.forEach(authCallbacks, function (callback) {
          callback();
        });
        transitTo('initialized');
        break;

      case 'passenger_assigned':
        if (state == 'initialized' || state == 'assigned') {
          transitTo('assigned', data);
        }
        break;

      case 'passenger_approved':
        transitTo('approved');
        break;

      case 'passenger_rejected':
        $ionicPopup.alert({
          title: '요청 거절',
          template: '기사님이 승객님의 요청을 거졀하였습니다 - ' + data.reason,
          okText: '확인'
        });
        transitTo('initialized');
        break;

      case 'passenger_progress':
        transitTo('approved', data);
        break;

      case 'passenger_journey':
        transitTo('boarded', data);
        break;

      case 'passenger_arrived':
        transitTo('arrived');
        break;

      case 'passenger_boarded':
        transitTo('boarded');
        break;

      case 'passenger_completed':
        transitTo('initialized');
        break;

      case 'passenger_disconnected':
        $ionicPopup.alert({
          title: '연결 끊김',
          template: '기사의 연결이 끊겼습니다.',
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
    watch: function () {
      var action = function () {
        send('passenger_watch', {
          charge_type: chargeType,
          location: [location.longitude, location.latitude]
        });
      };
      !!location ? action() : this.onLocationChange(action, true);
    },
    request: function (driverId) {
      send('passenger_request', {
        driver_id: driverId,
        source: {
          address: null,
          poi: null,
          location: [location.longitude, location.latitude]
        },
        destination: {
          address: '서울시 강남구 삼성동',
          poi: '삼성역',
          location: [127.0631652, 37.5088693]
        }
      });
      transitTo('requested');
    },
    cancel: function (reason) {
      send('passenger_cancel', {
        reason: reason
      });
      transitTo('initialized');
    },
    rate: function (rating, comment) {
      send('passenger_rate', {
        rating: rating,
        comment: comment
      });
    },
    changeChargeType: function (chargeType_) {
      chargeType = chargeType_;
      this.watch();
    },

    onLocationChange: function (callback, once) {
      if (once) {
        var tentative = function () {
          callback();
          locationCallbacks.splice(locationCallbacks.indexOf(tentative), 1);
        };
        locationCallbacks.push(tentative);
      } else {
        locationCallbacks.push(callback);
      }
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
    '$scope', '$http', '$location', '$ionicViewService', '$ionicLoading', '$ionicPopup',
    'Auth', 'Passenger',
    function ($scope, $http, $location, $ionicViewService, $ionicLoading, $ionicPopup,
              Auth, Passenger) {
  $scope.data = {};
  $scope.submit = function () {
    var passenger = new Passenger($scope.data);
    $ionicLoading.show({ template: '<div class="spinner"></div>' });
    $http.post('/api/passengers/signup', $scope.data).then(function () {
    //passenger.$save().then(function () {
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
    '$scope', '$http', '$ionicPopup', 'locationHost', 'Session',
    function ($scope, $http, $ionicPopup, locationHost, Session) {
  $scope.located = false;
  $scope.map = {
    control: {},
    center: {
      latitude: 0,
      longitude: 0
    },
    zoom: 15
  };
  $scope.data = {};
  $scope.location = {};
  $scope.state = null;
  $scope.taxiIcon = 'img/taxi.png';

  // For 'assigned' state
  $scope.assignment = {};

  // For 'approved' state
  $scope.driver = {
    location: {}
  };

  $scope.requestBest = function () {
    Session.request($scope.assignment.best.driver.id);
  };
  $scope.requestCandidates = function () {
    // FIXME: Implement
  };
  $scope.changeChargeType = function () {
    Session.changeChargeType($scope.data.charge_type)
  };
  $scope.call = function () {
    $ionicPopup.alert({
      title: '전화걸기',
      template: '전화걸기',
      okText: '확인'
    });
  };
  $scope.cancel = function () {
    $ionicPopup.confirm({
      title: '콜 취소',
      template: '정말 취소하시겠습니가? 평가에 부정적으로 반영됩니다.',
      okText: '취소',
      cancelText: '돌아가기'
    }).then(function (confirm) {
      if (confirm) {
        Session.cancel();
      }
    });
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
        case 'initialized':
          Session.watch();
          break;

        case 'assigned':
          $scope.assignment = data.assignment;
          break;

        case 'requested':
          $scope.assignment = {};
          break;

        case 'approved':
          data && data.location && ($scope.driver.location = data.location);
          break;

        case 'boarded':
          data && data.location && ($scope.driver.location = data.location);
          break;
      };
    });
    Session.initialize();
  };

  init();
}]);

;
