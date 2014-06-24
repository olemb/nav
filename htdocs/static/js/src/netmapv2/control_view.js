define([
    'netmap/collections',
    'netmap/models',
    'netmap/graph',
    'libs/backbone',
    'libs/backbone-eventbroker'
], function (Collections, Models, Graph) {

    var ControlView = Backbone.View.extend({

        el: '#navigation-view',
        interests: {
            'netmap:graphDoneLoading': 'initNetmapView'
        },
        events: {
            'click .filter-category': 'updateCategoryFilter'
        },

        initialize: function () {

            // Initialize the available views from the
            // window-object.
            this.netmapViews = new Collections.NetmapViewCollection();
            this.netmapViews.reset(window.netmapData.views);
            this.currentView = this.netmapViews.get(window.netmapData.defaultView);

            this.grabControlsFromDOM();

            Backbone.EventBroker.register(this);
        },

        /**
         * Grabs and caches the elements belonging to this view
         * from the DOM, and binds the necessary events.
         */
        grabControlsFromDOM: function () {
            var self = this;
            
            this.graphSearchInput = this.$('#graph-search-input');
            this.graphSearchSubmit = this.$('#graph-search-submit');
            this.graphSearchSubmit.click(this, this.searchGraph);

            // TODO: Find a cleaner way to set the selected option
            this.graphLayerSelect = this.$('#graph-layer-select');
            $('option', this.graphLayerSelect).each(function (i, option) {
                if (self.currentView.get('topology') === parseInt(option.value)) {
                    option.selected = true;
                }
            });
            this.graphLayerSelect.change(this, this.changeTopologyLayer);

            this.graphViewSelect = this.$('#graph-view-select');
            $('option', this.graphViewSelect).each(function (i, option) {
                if (self.currentView.id === parseInt(option.value)) {
                    option.selected = true;
                }
            });
            this.graphViewSelect.change(this, this.changeNetmapView);

            this.navigationSubViewToggle = this.$('#sub-view-toggle');
            this.navigationSubView = this.$('#navigation-sub-view');
            this.navigationSubViewToggle.click(function () {
                $('i', self.navigationSubViewToggle).toggleClass('fa-caret-down fa-caret-up');
                self.navigationSubView.toggle();
            });

            this.advancedOptionsToggle = this.$('#advanced-options-toggle');
            this.advancedOptions = this.$('#advanced-options');
            this.advancedOptionsToggle.click(function () {
                $('i', self.advancedOptionsToggle).toggleClass('fa-caret-down fa-caret-up');
                self.advancedOptions.toggle();
            });

            _.each(this.currentView.get('categories'), function (category) {
                self.$('#filter-' + category).prop('checked', true);
            });
        },

        /**
         * Triggers when the topology layer is changed. Updates the
         * view and fires an event to the graph model
         * @param e
         */
        changeTopologyLayer: function (e) {

            var self = e.data;

            var newValue = parseInt(self.graphLayerSelect.val());
            var oldValue = self.currentView.get('topology');

            if (newValue !== oldValue) {

                self.currentView.set('topology', newValue);

                Backbone.EventBroker.trigger('netmap:topologyLayerChanged', newValue);
            }
        },

        /**
         *
         */
        initNetmapView: function () {
           Backbone.EventBroker.trigger('netmap:netmapViewChanged', this.currentView);
        },

        /**
         * Triggers when the current netmap view is changed
         * @param e
         */
        changeNetmapView: function (e) {

            var self = e.data;

            var newValue = parseInt(self.graphViewSelect.val());
            var oldValue = self.currentView.id;

            if (newValue !== oldValue) {

                self.currentView = self.netmapViews.get(newValue);

                // Update category checkboxes
                var newCategories = self.currentView.get('categories');
                _.each(self.$('.filter-category'), function (elem) {
                    if (_.contains(newCategories, elem.value)) {
                        elem.checked = true;
                    } else {
                         elem.checked = false;
                    }
                });

                Backbone.EventBroker.trigger('netmap:netmapViewChanged', self.currentView);
            }
        },

        /**
         * Triggers when a new category is selected. Updates the
         * current view and notifies the graph.
         * @param e
         */
        updateCategoryFilter: function (e) {

            var categoryId = e.currentTarget.value;
            var checked = e.currentTarget.checked;
            var categories = this.currentView.get('categories');

            if (checked) {
                categories.push(categoryId);
            } else {
                categories.splice(categories.indexOf(categoryId), 1);
            }

            Backbone.EventBroker.trigger('netmap:filterCategoriesChanged', categoryId, checked);
        },

        /**
         * Triggers a graph search for the given query
         * @param e
         */
        searchGraph: function (e) {
            e.preventDefault();

            var self = e.data;
            var query = self.graphSearchInput.val();

            Backbone.EventBroker.trigger('netmap:netmapGraphSearch', query);
        }
    });

    return ControlView;
});