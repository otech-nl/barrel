from flask_sqlalchemy import SQLAlchemy
from pprint import pformat
from sqlalchemy.orm import backref
from sqlalchemy.ext.associationproxy import association_proxy
import inflect

########################################


def enable(app):  # noqa: C901

    if app.config['SQLALCHEMY_DATABASE_URI'] == 'default':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s.db' % app.name
    app.logger.info('Enabling DB with %s' % app.config['SQLALCHEMY_DATABASE_URI'])

    app.db = SQLAlchemy(app)  # session_options={'autocommit': False, 'autoflush': False}
    app.inflect = inflect.engine()
    db = app.db

    db.echo = app.config['DEBUG']

    class CRUDMixin(object):

        delay_save = False

        @classmethod
        def __clean_kwargs(cls, kwargs):
            cols = cls.__dict__
            rem = [k for k in kwargs
                   if k not in cols and '_%s' % k not in cols and '%s_id' % k not in cols]
            for r in rem:
                del kwargs[r]

        @classmethod
        def create(cls, commit=True, report=True, **kwargs):
            if report:
                app.logger.report('Creating %s: %s' % (cls.__name__, pformat(kwargs)))
            cls.__clean_kwargs(kwargs)
            obj = cls(**kwargs)
            obj.before_create(kwargs)
            db.session.add(obj)
            obj.save(commit)
            obj.after_create(kwargs)
            return obj

        def update(self, commit=True, report=True, **kwargs):
            if report:
                app.logger.report('Updating %s "%s": %s' % (self.__class__.__name__,
                                                            self,
                                                            pformat(kwargs)))
            self.__clean_kwargs(kwargs)
            # print 'UPDATE %s' % self
            # print '   %s' % kwargs
            self.before_update(kwargs)
            for attr, value in kwargs.items():
                setattr(self, attr, value)
            self.save(commit)
            self.after_update(kwargs)
            return self

        def save(self, really=True):
            if really and not self.delay_save:
                db.session.commit()
            return self

        def delete(self, commit=True, report=True):
            if report:
                app.logger.report('Deleting %s "%s"' % (self.__class__.__name__, self))
            db.session.delete(self)
            self.after_delete()
            return commit and db.session.commit()

        def before_create(self, values):
            pass

        def after_create(self, values):
            pass

        def before_update(self, values):
            pass

        def after_update(self, values):
            pass

        def after_delete(self):
            pass

        @classmethod
        def bulk_insert(cls, new_records):
            print('Bulk insert of %s: %s' % (cls.__name__, new_records))
            max_id = cls.get_max_id()
            for rec in new_records:
                if id not in rec:
                    max_id += 1
                    rec['id'] = max_id
            db.engine.execute(cls.__table__.insert(), new_records)
            cls.commit()

    db.CRUDMixin = CRUDMixin

    class NamingMixin(object):

        @classmethod
        def columns(cls):
            return cls.__table__.columns.keys()

        def to_dict(self):
            return {c.name: getattr(self, c.name) for c in self.__table__.columns}

        @classmethod
        def get_api(cls):
            return cls.__tablename__

        @classmethod
        def get_plural(cls):
            return app.inflect.plural(cls.get_api())


    db.NamingMixin = NamingMixin

    class OperationsMixin(object):

        @classmethod
        def get(cls, id):
            return db.session.query(cls).get(id)

        @classmethod
        def get_by(cls, key, val, one=True, or_none=True):
            rec = db.session.query(cls).filter(getattr(cls, key) == val)
            if one:
                if or_none:
                    return rec.one_or_none()
                else:
                    return rec.one()
            else:
                return rec.all()

        @classmethod
        def get_or_404(cls, id):
            return db.session.query(cls).get_or_404(id)

        @classmethod
        def from_form(cls, form):
            obj = cls()
            form.populate_obj(obj)
            return obj

        @classmethod
        def get_max_id(cls):
            return db.session.query(db.func.max(cls.id)).scalar() or 0

        @staticmethod
        def commit():
            # print('DIRTY: %s' % db.session.dirty)
            # print('NEW: %s' % db.session.new)
            # print('DELETED: %s' % db.session.deleted)
            db.session.commit()

        @staticmethod
        def rollback():
            db.session.rollback()

    db.OperationsMixin = OperationsMixin

    class BaseModel(db.Model, NamingMixin):
        ''' used as super model for all other models '''
        __abstract__ = True

        id = db.Column(db.Integer, primary_key=True)

        @classmethod
        def make_supermodel(cls, identities=[]):
            print('Making supermodel %s: %s' % (cls.__name__, identities))
            cls.identities = identities
            cls.discrimator = db.Column(db.Enum(*cls.identities))
            cls.__mapper_args__ = {
                'polymorphic_identity': 'base',
                'polymorphic_on': 'discrimator',
                'with_polymorphic': '*'
            }

        @classmethod
        def derive_model(cls, derived_cls, identity=None, single_table=True):
            print('Derive model %s < %s' % (derived_cls.__name__, cls.__name__))
            attrs = dict(__mapper_args__={'polymorphic_identity': identity or derived_cls.__name__})
            if single_table:
                print('   single table: %s.id' % cls.__tablename__)
                attrs['id'] = db.Column(db.Integer,
                                         db.ForeignKey('%s.id' % cls.__tablename__),
                                         primary_key=True)
            derived_cls = type(derived_cls.__name__, (derived_cls, cls), attrs)
            return derived_cls

        @classmethod
        def add_reference(cls, peer_cls, name=None, rev_name='', nullable=False, one_to_one=False,
                          rev_cascade='save-update, merge, delete', default=None, add_backref=True):
            ''' relation scaffolding with sensible defaults '''
            name = name or peer_cls.__tablename__
            foreign_key = '%s_id' % name

            # create foreign key
            setattr(cls,
                    foreign_key,
                    db.Column(db.Integer,
                              db.ForeignKey('%s.id' % peer_cls.__tablename__),
                              default=default,
                              nullable=nullable))

            # prepare optional relation kwarg
            kwargs = dict()
            if add_backref:
                rev_name = rev_name or (cls.get_api() if one_to_one else cls.get_plural())
                kwargs['backref'] = backref(rev_name,
                                            lazy='dynamic',
                                            cascade=rev_cascade,
                                            uselist=not one_to_one)
            print('Referencing %s.%s -> %s (%s%s)'
                  % (cls.__name__, name, peer_cls.__name__, rev_name, '' if one_to_one else '*'))
            # create relationship
            setattr(cls, name, db.relationship(peer_cls.__name__,
                                               foreign_keys=[getattr(cls, foreign_key)],
                                               remote_side=peer_cls.id,
                                               **kwargs))

        @classmethod
        def add_cross_reference(cls, peer_cls, names=None, x_names=None, x_cls=None):
            ''' adds an m:n relation between this class and peer_cls '''
            names = names or (cls.__tablename__, peer_cls.__tablename__)
            x_names = x_names or (app.inflect.plural(names[1]), app.inflect.plural(names[0]))

            # create cross reference table
            x_cls = x_cls or type(cls.__name__ + peer_cls.__name__, (db.BaseModel,), {})
            x_cls.add_reference(cls, name=names[0], add_backref=False)
            x_cls.add_reference(peer_cls, name=names[1], add_backref=False)

            print('   cross reference: %s.%s <-> %s.%s' %
                  (cls.__name__, x_names[0], peer_cls.__name__, x_names[1]))

            # create relationship
            if cls == peer_cls:
                # self-referential
                setattr(cls, x_names[0], association_proxy(x_names[1], names[0]))
                setattr(cls, x_names[1], association_proxy(x_names[0], names[1]))
            else:
                setattr(cls, x_names[0],
                        db.relationship(
                            peer_cls.__name__,
                            secondary=x_cls.__tablename__,
                            backref=db.backref(x_names[1], lazy='dynamic')))

            return x_cls

        @classmethod
        def add_enum_reference(cls, peer_cls, **kwargs):
            kwargs.setdefault('nullable', True)
            kwargs.setdefault('name', peer_cls.__tablename__[5:])
            return cls.add_reference(peer_cls, **kwargs)

    db.BaseModel = BaseModel

    return db

########################################


def supermodel(identities=None):
    def class_decorator(cls):
        cls.make_supermodel(identities)
        return cls
    return class_decorator


def extend_model(super_cls, identity=None, single_table=True):
    ''' decorator for  super_cls.derive_model '''
    def class_decorator(cls):
        return super_cls.derive_model(cls, identity, single_table)
    return class_decorator


def add_reference(peer_cls, **kwargs):
    ''' decorator for to cls.add_reference '''
    def class_decorator(cls):
        cls.add_reference(peer_cls, **kwargs)
        return cls
    return class_decorator


def add_cross_reference(peer_cls=None, **kwargs):
    ''' decorator for to cls.add_cross_reference '''
    def class_decorator(cls):
        cls.add_cross_reference(peer_cls or cls, **kwargs)
        return cls
    return class_decorator


def cross_reference(cls, peer_cls, **kwargs):
    ''' decorator for to x_cls.add_reference '''
    def class_decorator(x_cls):
        cls.add_cross_reference(peer_cls, x_cls=x_cls, **kwargs)
        return x_cls
    return class_decorator


def add_enum_reference(peer_cls, **kwargs):
    ''' decorator for to cls.add_enum_reference '''
    def class_decorator(cls):
        cls.add_enum_reference(peer_cls, **kwargs)
        return cls
    return class_decorator

########################################


def init(app):
    app.logger.info('Initializing DB %s' % app.db)
    app.db.drop_all()
    app.db.create_all()
