var app = app || {};

String.prototype.ucfirst = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

app.Collection = function(element, modelData) {
  // copy row to form when clicked
  var ClickableRow = Backgrid.Row.extend({
    events: {
      "click": function (event) {
        var attrs = this.model.attributes;
        var keys = _.keys(attrs);
        _.forEach(keys, function(attr) {
          var val = attrs[attr];
          var tag = "form#edit #"+attr;
          var el = $(tag);
          var type = el.prop('tagName');
          if( type == 'TEXTAREA' ) {
            el.html(val);
          } else if(type == 'SELECT') {
            $(tag+" option").filter(function(key, option) {
              return (option.text == val);
            }).attr('selected', true);
          } else {
            el.val(attrs[attr]);
          }
        });
      }
    }
  });

  // a model that saves changes
  var Model = Backbone.DeepModel.extend({
      initialize: function() {
        this.on('backgrid:edited', this.didEdit, this);
      },

      didEdit: function (model, cell, command) {
        console.log("Saving");
        result = model.save(null, {
          error: function(model, response, options) {
            if(response.status == 404 || response.status == 405) {
              alert("Fout: "+response.statusText+" ("+response.status+")");
            }
            else {
              console.log(response.responseText);
              text = JSON.parse(response.responseText);
              alert("Fout: "+text.message);
            }
          }
        });
      }
  });

  // a collection that connects to REST
  var Collection = Backbone.PageableCollection.extend({
    model: Model,
    parseRecords: function(response) {
      return response.objects;
    },
    url: '/api/'+modelData.api,
    state: {
      pageSize: 10,
      sortKey: 'id'
    },
    queryParams: {
      totalRecords: null,
      totalPages: null,
      sortKey: null,
      order: null,
      currentPage: "page",
      sortKey: "sort",
      order: "order",
      pageSize: null,
      q: function () {
        if(this.state.sortKey) {
          $.extend(this.filters, {
            order_by: [{
              field: this.state.sortKey,
              direction: this.state.order == -1 ? "asc" : "desc"
            }]
          });
        }
        var filters = JSON.stringify(this.filters);
        return filters;
      }
    },

    parseState: function (resp, queryParams, state, options) {
        return {
          totalRecords: resp.num_results,
        };
    }
  });

  this.load_grid = function() {
    var filters = modelData.filters;
    if(_.has($.fn, 'apply_filter')) {
      filters = filters.concat($.fn.apply_filter());
    }
    // if we have filters, format them properly
    if(filters && filters.length > 0) {
      this.collection.filters = {filters: filters};
    } else {
      this.collection.filters = {}
    }

    this.collection.fetch({
      reset: true,
      success: function(collection, response, options) {
        var result = grid.render().el;
        $(element).html(result);
        if(collection.state.totalPages > 1) {
          var paginator = new Backgrid.Extension.Paginator({
            collection: collection
          });
          $(element).append(paginator.render().el);
        }
      },
      error: function(collection, response, options) {
        $('body').html(response.responseText);
      }

    });
  };

  function format_statusbar() {
    return {
      name: 'statusbar',
      label: 'Status',
      editable: false,
      sortable: false,
      cell: Backgrid.Cell.extend({
        className: "statusbar-cell",
        render: function () {
          var values = this.model.get('get_status')
          var html = formatStatusbar(values);
          this.$el.empty();
          this.$el.html( html );
          this.delegateEvents();
          return this;
        }
      })
    };
  }

  function format_toolbar(tools) {
    return {
      name: 'toolbar',
      label: 'Acties',
      editable: false,
      sortable: false,
      cell: Backgrid.Cell.extend({
        className: "toolbar-cell",
        render: function () {
          var id = this.model.id;
          var html = tools.map(function(tool) {
            return '<a href="/toolbar/'+modelData.modelName+'/'+tool+'/'+id+'" class="'+tool+'"><img src="/static/img/icon_'+tool+'.png"></a>';
          });
          this.$el.empty();
          this.$el.html( html.join('') );
          this.delegateEvents();
          return this;
        }
      })
    };
  }

  // prepare columns array
  modelData.columns = modelData.columns.map( function(column, index) {
    if(typeof column === "string") {
      column = {'name': column};
    }
    if(!_.has(column,"cell")) {
      column.cell = "string";
    }
    if(!_.has(column,"editable")) {
      column.editable = false;
    }
    if(column.cell === 'select') {
      if(typeof column.options[0] === 'string'){
        column.options = column.options.map(function(column) {
          return [column, column];
        });
      }
      // console.log(column);
      column.cell = Backgrid.SelectCell.extend({
        optionValues: column.options
      });
    }
    if(column.cell === "toolbar") {
      column = format_toolbar(column.tools);
    } else if(column.cell === "statusbar") {
        column = format_statusbar();
    } else if(column.cell === "date") {
      column.formatter = _.extend({}, Backgrid.CellFormatter.prototype, {
        fromRaw: function (rawValue, model) {
          return new Date(rawValue).pretty_print();
        }
      });
      column.sortable = true;
    } else if(column.cell === "datetime") {
      column.formatter = _.extend({}, Backgrid.CellFormatter.prototype, {
        fromRaw: function (rawValue, model) {
          return new Date(rawValue).pretty_print(true);
        }
      });
      column.sortable = true;
    } else if(column.cell === "boolean") {
      column.cell = Backgrid.BooleanCell.extend({});
    }
    if(!("label" in column)) {
      column.label = column.name.replace(/^get_/, "").split('_').join(' ').ucfirst();
    }
    if(column.name.match(/^get_/)) {
      column.sortable = false;
    }
    return column;
  });


  this.collection = new Collection();
  var grid = new Backgrid.Grid({
    columns: modelData.columns,
    collection: this.collection,
    row: ClickableRow
  });
  this.load_grid();
  var collection = this;

  $('button#filter').click(function (event) {
    collection.load_grid();
  });

  $('button#new'+modelData.modelName).click(function (event) {
    $('button#new'+modelData.modelName).hide();
    $('div#new'+modelData.modelName).show();
  });

  $('button#cancel'+modelData.modelName.toLowerCase()).click(function (event) {
    $('button#new'+modelData.modelName).show();
    $('div#new'+modelData.modelName).hide();
  });

  $('div.backgrid-container').on('click', 'a.delete', function(event) {
    if(!confirm('Weet u het zeker? (Dit item en alle gerelateerde items worden definitief verwijderd!)')) {
      event.preventDefault();
      event.stopPropagation();
    }
  });
};
