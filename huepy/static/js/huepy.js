(function() {

App.Models.LightsEvent = Backbone.Model.extend({
    url: function() { return '/event/lights'; }
});

//TODO: move this into the main app
App.AlertView = Backbone.View.extend({
    success: function(msg) {
        this.$el.text(msg)
            .removeClass('alert-warning alert-info alert-danger hidden')
            .addClass('alert-success');
    },
    fail: function(msg) {
        this.$el.text(msg)
            .removeClass('alert-success alert-info alert-warning hidden')
            .addClass('alert-danger');
    }
});
var config_alert = new App.AlertView({el: '#config-alert'});


var LightCtrlView = Backbone.View.extend({
  events: {
      'click': 'performAction'
  },
  initialize: function(options) {
      this.data = options.data;
  },
  performAction: function(ev) {
      var ev = new App.Models.LightsEvent(this.data);
      ev.save();
  }
});

var allon = new LightCtrlView({
    el: '#btn-all-on',
    data: {target: 'group', id: '0', on:true}
});
var alloff = new LightCtrlView({
    el: '#btn-all-off',
    data: {target: 'group', id: '0', on:false}
});

var DiscoverHubView = Backbone.View.extend({
    el: '#btn-discover',
    events: {
        'click': 'discover'
    },
    discover: function(ev) {
        //TODO: this is should be implemented with models/views
        $.get('discover', function(response) {
            $("#txt-ip-address").val(response).focus();
        });
    }
})
var discover = new DiscoverHubView();

var RegisterAppView = Backbone.View.extend({
    el: '#btn-register',
    events: {
        'click': 'register'
    },
    register: function(ev) {
        //TODO: this is should be implemented with models/views
        $.get('register', function(response) {
            config_alert.success('Registered app successfully');
        })
        .fail(function(response) {
            config_alert.fail('Failed to register with hub: ' +
              response.responseText);
        });
    }
})
var register = new RegisterAppView();

var TestHubView = Backbone.View.extend({
    el: '#btn-test-hub',
    events: {
        'click': 'test'
    },
    test: function(ev) {
        $.get('test', function(response) {
            config_alert.success('Connected to hub');
        })
        .fail(function() {
            config_alert.fail('Failed to connect to hub');
        });
    }
});
var testhub = new TestHubView();

})();
