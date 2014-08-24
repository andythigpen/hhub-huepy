(function() {

App.Models.LightsEvent = Backbone.Model.extend({
    url: function() { return '/event/lights'; }
});

var LightCtrl = Backbone.View.extend({
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

var allon = new LightCtrl({el: '#btn-all-on', data: {target: 'group', id: '0', on:true}});
var alloff = new LightCtrl({el: '#btn-all-off', data: {target: 'group', id: '0', on:false}});

})();
