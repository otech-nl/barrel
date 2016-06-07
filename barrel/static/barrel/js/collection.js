var app = app || {};

String.prototype.ucfirst = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}

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
            if(response.status == 404 || response.status == 405)
              alert("Fout: "+response.statusText+" ("+response.status+")");
            else {
              console.log(response.responseText);
              text = JSON.parse(response.responseText);
              alert("Fout: "+text["message"]);
            }
          },
        });
      }
  });

  // a collection that connects to REST
  var Collection = Backbone.Collection.extend({
    model: Model,
    parse: function(response) {
      return response.objects;
    },
    url: '/api/'+modelData.api
  });

  this.load_grid = function() {
    var filters = []
    modelData.filters.forEach(function(element) {
      filters.push(element);
    })
    if(_.has(app, 'filters')) {
      filters = filters.concat(app.filter());
    }

    // if we have filters, format them properly
    if(filters && filters.length > 0)
      filters = 'q='+JSON.stringify({filters: filters});

    this.collection = new Collection();
    var grid = new Backgrid.Grid({
      columns: modelData.columns,
      collection: this.collection,
      row: ClickableRow
    });
    result = grid.render().el;
    $(element).html(result);

    // console.log(filters)
    this.collection.fetch({reset: true, data: filters});
  }

  function format_statusbar() {
    function statusbar_cell(size, cls, value) {
      return '<td width='+size+' class="'+cls+'" align="center">'+value+'</td>'
    }
    return {
      name: 'statusbar',
      label: 'Status',
      editable: false,
      cell: Backgrid.Cell.extend({
        className: "statusbar-cell",
        render: function () {
          var values = _.pairs(this.model.get('get_status'));
          var sum = values.reduce(function(prev, curr) {
            return prev + curr[1];
          }, 0);
          var id = this.model.id;
          var html = values.map(function(value) {
            if(value[1])
              return statusbar_cell(Math.round(100*value[1]/(sum+1))+'%', value[0], value[1]);
            else
              return '';
          });
          html.push(statusbar_cell(20, 'sum', sum));
          html = '<table width=200><tr>'+html.join('')+'</tr></table>';
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
    };
    if(column.cell === "toolbar") {
      column = format_toolbar(column.tools);
    } else if(column.cell === "statusbar") {
        column = format_statusbar();
    } else if(column.cell === "date") {
      console.log('DATE');
      column.cell = Backgrid.DateCell.extend({});
    } else if(column.cell === "datetime") {
      column.cell = Backgrid.DatetimeCell.extend({});
    } else if(column.cell === "boolean") {
      column.cell = Backgrid.BooleanCell.extend({});
    };
    if(!_.has(column,"label")) {
      column.label = column.name.split('_').join(' ').ucfirst();
    }
    return column;
  });

  this.load_grid();
  var collection = this;

  $('button#filter').click(function (event) {
    console.log('Filtering');
    collection.load_grid();
  })

  $('button#new'+modelData.modelName).click(function (event) {
    $('button#new'+modelData.modelName).hide();
    $('div#new'+modelData.modelName).show();
  })

  $('button#cancel'+modelData.modelName.toLowerCase()).click(function (event) {
    $('button#new'+modelData.modelName).show();
    $('div#new'+modelData.modelName).hide();
  })

  $('div.backgrid-container').on('click', 'a.delete', function(event){
    console.log('DELETE');
    if(!confirm('Weet u het zeker? (Dit item en alle gerelateerde items worden definitief verwijderd!)')) {
      console.log('   CANCEL');
      event.preventDefault();
      event.stopPropagation();
    } else {
      console.log('   GO');
    }
  })
}
