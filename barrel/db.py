from flask_sqlalchemy import SQLAlchemy
from pprint import pformat
from sqlalchemy.orm import backref

########################################


def enable(app):  # noqa: C901

    if app.config['SQLALCHEMY_DATABASE_URI'] == 'default':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s.db' % app.name
    app.logger.info('Enabling DB with %s' % app.config['SQLALCHEMY_DATABASE_URI'])

    app.db = SQLAlchemy(app)  # session_options={'autocommit': False, 'autoflush': False}
    db = app.db

    db.echo = app.config['DEBUG']

    class CRUDMixin(object):

        delay_save = False

        @classmethod
        def __clean_kwargs(cls, kwargs):
            cols = cls.__dict__
            rem = [k for k in kwargs if k not in cols and '_%s' % k not in cols and '%s_id' % k not in cols]
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

    db.CRUDMixin = CRUDMixin

    class BaseModel(db.Model):
        ''' used as super model for all other models '''
        __abstract__ = True

        id = db.Column(db.Integer, primary_key=True)

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
        def add_reference(cls, peer, name=None, rev_name=None, nullable=False, one_to_one=False,
                          rev_cascade='save-update, merge, delete', default=None):
            ''' bundles all the paperwork for making a relation and provides some sensible defaults '''
            peer_name = peer.__tablename__
            name = name or peer_name
            rev_name = rev_name or (cls.__tablename__ if one_to_one else cls.__tablename__ + 's')
            foreign_key = '%s_id' % name
            # print('Setting attr [%s] through fk [%s] to peer [%s] (rev=[%s]%s)'
            #       % (name, foreign_key, peer_name, rev_name, '' if one_to_one else '*'))
            setattr(cls,
                    foreign_key,
                    db.Column(db.Integer,
                              db.ForeignKey('%s.id' % peer_name),
                              default=default,
                              nullable=nullable))
            setattr(cls,
                    name,
                    db.relationship(peer.__name__,
                                    backref=backref(rev_name,
                                                    lazy='dynamic',
                                                    cascade=rev_cascade,
                                                    uselist=not one_to_one),
                                    foreign_keys=[getattr(cls, foreign_key)],
                                    remote_side=peer.id))

        @classmethod
        def add_enum_reference(cls, peer, **kwargs):
            kwargs.setdefault('nullable', True)
            kwargs.setdefault('name', peer.__tablename__[5:])
            return cls.add_reference(peer, **kwargs)

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
            return db.session.query(db.func.max(cls.id)).scalar() or 0

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

        @staticmethod
        def commit():
            # print('DIRTY: %s' % db.session.dirty)
            # print('NEW: %s' % db.session.new)
            # print('DELETED: %s' % db.session.deleted)
            db.session.commit()

        @staticmethod
        def rollback():
            db.session.rollback()

    db.BaseModel = BaseModel

    return db


def init(app):
    app.logger.info('Initializing DB %s' % app.db)
    app.db.drop_all()
    app.db.create_all()
