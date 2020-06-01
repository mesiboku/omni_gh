odoo.define('omni_gh_production_schedule.equipments_summary', function (require) {
'use strict';

var core = require('web.core');
var basicFields = require('web.basic_fields');
var FieldText = basicFields.FieldText;
var registry = require('web.field_registry');

var QWeb = core.qweb;
var _t = core._t;

var MyWidget = FieldText.extend({

    init: function () {
        this._super.apply(this, arguments);
        if (this.mode === 'edit') {
            this.tagName = 'span';
        }
        this.set({
            summary_header: py.eval(this.recordData.summary_header),
            equipments_summary: py.eval(this.recordData.equipments_summary ),
        });
    },
    start: function() {
        var self = this;
        if (self.setting)
            return;
        
        if (! this.get("summary_header") || ! this.get("equipments_summary"))
               return
               
        this.renderElement();
        // this.view_loading();
     },
     // view_loading: function(r) {
     //     return this.load_form(r);
     // },
     // load_form: function(data) {
     //     var self = this
     //     this.$el.find(".table_free").bind("click", function(event){
     //         self.do_action({
     //                 type: 'ir.actions.act_window',
     //                 res_model: "quick.room.reservation",
     //                 views: [[false, 'form']],
     //                 target: 'new',
     //                 context: {"room_id": $(this).attr("data"), 'date': $(this).attr("date"), 'default_adults': 1},
     //         });
     //     });
     // },
     renderElement: function() {
         this._super();
         this.$el.html(QWeb.render("EquipmentSummary", {widget: this}));
    },
    reset: function (record, event) {
        var res = this._super(record, event);
        this.set({
            "summary_header": py.eval(this.recordData.summary_header),
            "equipments_summary":py.eval(this.recordData.equipments_summary)
        });
        this.renderElement();
        // this.view_loading();
        return res;
    },

});

registry.add(
    'Equipments_summary', MyWidget
);
return MyWidget
});
