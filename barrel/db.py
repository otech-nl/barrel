from flask_sqlalchemy import SQLAlchemy

########################################

def enable(app):
    if app.config['SQLALCHEMY_DATABASE_URI'] == 'default':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s.db' % app.name
    app.logger.info('Enabling DB with %s' % app.config['SQLALCHEMY_DATABASE_URI'])

    app.db = SQLAlchemy(app)
    db = app.db

    db.echo = app.config['DEBUG']

    class CRUDMixin(object):
        @classmethod
        def __clean_kwargs(cls, kwargs):
            cols = cls.__dict__
            rem = []
            for k in kwargs:
                if not k in cols and not '_%s'%k in cols and not '%s_id'%k in cols:
                    rem.append(k)
            for r in rem:
                del kwargs[r]

        @classmethod
        def create(cls, commit=True, **kwargs):
            print 'CREATE %s' % cls
            cls.__clean_kwargs(kwargs)
            print '   %s' % kwargs
            instance = cls(**kwargs)
            obj = instance.save(commit=commit)
            obj.after_create()
            return obj

        @classmethod
        def get(cls, id):
            return cls.query.get(id)

        @classmethod
        def get_or_404(cls, id):
            return cls.query.get_or_404(id)

        def update(self, commit=True, **kwargs):
            self.__clean_kwargs(kwargs)
            print 'UPDATE %s' % self
            # print '   %s' % kwargs
            for attr, value in kwargs.iteritems():
                setattr(self, attr, value)
            return commit and self.save() or self

        def save(self, commit=True):
            db.session.add(self)
            if commit:
                db.session.commit()
            return self

        def delete(self, commit=True):
            db.session.delete(self)
            return commit and db.session.commit()

        def after_create(self):
            pass
    db.CRUDMixin = CRUDMixin

    class BaseModel(db.Model):
        ''' used as super model for all other models '''
        __abstract__ = True

        id = db.Column(db.Integer, primary_key=True)

        @classmethod
        def columns(cls):
            return cls.__table__.columns.keys()

        @classmethod
        def from_form(cls, form):
            obj = cls()
            form.populate_obj(obj)
            return obj

        def to_dict(self):
            return {c.name: getattr(self, c.name) for c in self.__table__.columns}

        @classmethod
        def get_api(cls):
            return cls.__tablename__

        @classmethod
        def get_max_id(cls):
            return db.session.query(db.func.max(cls.id)).scalar()

        @staticmethod
        def commit():
            db.session.commit()

    db.BaseModel = BaseModel

    return db

def init(app):
    app.logger.info('Initializing DB')
    app.db.create_all()
