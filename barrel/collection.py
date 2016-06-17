from flask import render_template, request
import forms

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
        super(ParentData, self).__init__(title, model_class, form_class)
        self.model = self.model_class.get(id)

    def handle_form(self):
        if self.api_name() in request.form:
            return forms.handle_form(self.model_class, self.form_class, model=self.model)
        else:
            return self.form_class(None, obj=self.model)

########################################

class ChildData(__CollectionModel):

    def __init__(self, title, model_class, form_class=None, columns=[], filters=[]):
        super(ChildData, self).__init__(title, model_class, form_class)
        self.columns = columns
        self.filters = filters

    def handle_form(self, parent):
        if self.api_name() in request.form:
            kwargs = dict()
            if parent:
                kwargs[parent.api_name()] = parent.model
            return forms.handle_form(self.model_class, self.form_class, **kwargs)
        else:
            return self.form_class()

########################################

def render(parent, children, template='barrel/collection.html', allow_add=True, **kwargs):
    title = ''
    if parent:
        kwargs[parent.form_name()] = parent.handle_form()
        title = parent.title

    if not type(children) is list:
        children = [children]

    children_data = []
    for child in children:
        kwargs[child.form_name()] = child.handle_form(parent)
        children_data.append(dict(
            modelName=child.model_name(),
            api=child.api_name(),
            subtitle=child.title,
            columns=child.columns,
            filters=child.filters,
            hide_subform=not kwargs[child.form_name()].errors,
            allow_add=allow_add,
        ))

    try:
        breadcrums = forms.breadcrums(parent.model.parent())
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
