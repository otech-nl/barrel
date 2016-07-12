from flask import render_template, request
from forms import BarrelForms

class BarrelCollection(object):

    def __init__(self, app):
        app.logger.info('Enabling %s' % self.__class__.__name__)
        self.app = app

    ########################################

    class __CollectionModel(object):

        def __init__(self, title, model_class, form_class=None):
            self.title = title
            self.model_class = model_class
            self.form_class = form_class or self.model_class.get_form()

        def model_name(self):
            return self.model_class.__name__

        def api_name(self):
            return self.model_class.get_api()

        def form_name(self):
            return '%s_form' % self.api_name()

    ########################################

    class ParentData(__CollectionModel):

        def __init__(self, id, title, model_class, form_class=None):
            super(BarrelCollection.ParentData, self).__init__(title, model_class, form_class)
            self.model = self.model_class.get(id)

        def handle_form(self, app):
            if self.api_name() in request.form:
                return app.forms.handle_form(self.model_class, self.form_class, model=self.model)
            else:
                return self.form_class(None, obj=self.model)

    ########################################

    class ChildData(__CollectionModel):

        def __init__(self, title, model_class, form_class=None, columns=[], filters=[]):
            super(BarrelCollection.ChildData, self).__init__(title, model_class, form_class)
            self.columns = columns
            self.filters = filters

        def handle_form(self, app, parent):
            if self.api_name() in request.form:
                kwargs = dict()
                if parent:
                    kwargs[parent.api_name()] = parent.model
                return app.forms.handle_form(self.model_class, self.form_class, **kwargs)
            else:
                return self.form_class()

    ########################################

    def render(self, parent, children, template='barrel/collection.html', allow_add=True, **kwargs):
        title = ''
        if parent:
            form = kwargs[parent.form_name()] = parent.handle_form(self.app)
            kwargs[parent.api_name()] = parent.model
            title = parent.title

        if not type(children) is list:
            children = [children]

        children_data = []
        for child in children:
            kwargs[child.form_name()] = child.handle_form(self.app, parent)
            children_data.append(dict(
                modelName=child.model_name(),
                api=child.api_name(),
                subtitle=child.title,
                columns=child.columns,
                filters=child.filters,
                hide_subform=not kwargs[child.form_name()].errors,
                allow_add=allow_add,
            ))

        # breadcrums = BarrelForms.breadcrums(parent.model.parent())
        try:
            breadcrums = BarrelForms.breadcrums(parent.model.parent())
        except Exception, e:
            breadcrums = None

        return render_template(
            template,
            title=title,
            breadcrums=breadcrums,
            parent=parent,
            children=children_data,
            **kwargs)

########################################

def enable(app):
    app.collection = BarrelCollection(app)
    return app.collection
