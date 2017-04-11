from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pprint import pformat

########################################


def enable(app):  # noqa: C901
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
            rem = []    # columns to be removed
            for k in kwargs:
                if k not in cols and '_%s' % k not in cols and '%s_id' % k not in cols:
                    rem.append(k)
            for r in rem:
                del kwargs[r]

        @classmethod
        def create(cls, commit=True, report=True, **kwargs):
            if report:
                app.logger.report('Creating %s: %s' % (cls.__name__, pformat(kwargs)))
            cls.__clean_kwargs(kwargs)
            obj = cls(**kwargs)
            obj.before_create()
            db.session.add(obj)
            if commit:
                obj.save()
            obj.after_create()
            return obj

        @classmethod
        def get(cls, id):
            return db.session.query(cls).get(id)

        @classmethod
        def get_or_404(cls, id):
            return cls.query.get_or_404(id)

        def update(self, commit=True, report=True, **kwargs):
            if report:
                app.logger.report('Updating %s "%s": %s' % (self.__class__.__name__,
                                                            self,
                                                            pformat(kwargs)))
            self.__clean_kwargs(kwargs)
            # print 'UPDATE %s' % self
            # print '   %s' % kwargs
            self.before_update()
            for attr, value in kwargs.iteritems():
                setattr(self, attr, value)
            if commit:
                self.save()
            self.after_update()
            return self

        def save(self):
            db.session.commit()
            return self

        def delete(self, commit=True):
            app.logger.report('Deleting %s "%s"' % (self.__class__.__name__, self))
            db.session.delete(self)
            return commit and db.session.commit()

        def before_create(self):
            pass

        def after_create(self):
            pass

        def before_update(self):
            pass

        def after_update(self):
            pass

    db.CRUDMixin = CRUDMixin

    class SoftDeleteMixin(CRUDMixin):

        ############################################
        # UNTESTED
        ############################################

        deleted_at = db.Column(db.DateTime, default=None)

        def delete(self, commit=True, undelete=False):
            print('############## SOFT DELETE')
            if undelete:
                self.deleted_at = None
            else:
                self.deleted_at = datetime.now()
            for rel in self.__mapper__.relationships:
                if 'delete' in rel._cascade:
                    relation = str(rel).split('.')[1]
                    relation = getattr(self, relation)
                    for obj in relation:
                        if isinstance(obj, SoftDeleteMixin):
                            obj.delete(commit=False, undelete=undelete)
                        else:
                            obj.delete(commit=False)

            return commit and db.session.commit()

        @classmethod
        def query(cls, *args, **kwargs):
            print('############## SOFT QUERY')
            if not args:
                query = cls._query(cls)
            else:
                query = cls._query(*args)

            if "include_deleted" not in kwargs or not kwargs["include_deleted"]:
                query = query.filter(cls.deleted_at is None)

            return query

        @classmethod
        def get(cls, id, include_deleted=False):
            return cls.query(include_deleted=include_deleted)\
                      .filter(cls.id == id)\
                      .first()

    db.SoftDeleteMixin = SoftDeleteMixin

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

        @staticmethod
        def rollback():
            db.session.rollback()

    db.BaseModel = BaseModel

    return db


def init(app):
    app.logger.info('Initializing DB')
    app.db.drop_all()
    app.db.create_all()
