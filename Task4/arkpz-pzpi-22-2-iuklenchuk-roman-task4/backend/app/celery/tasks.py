from celery import Task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.database.conn import url
# TODO: remove and use from config
sqlalchemy_url = url
sqlalchemy_url = url.replace("asyncpg", "psycopg2")
engine = create_engine(sqlalchemy_url, pool_recycle=3600, pool_size=10)

class DatabaseTask(Task):
    """An abstract Celery Task that ensures that the connection to the
    database is closed on task completion"""
    abstract = True

    def __init__(self):
        self._session = None
        self._fns_after_return = []

    @property
    def session(self):
        if self._session is None:
            self._session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        return self._session

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        if self._session is not None:
            self._session.commit()
            self._session.remove()
        super().after_return(status, retval, task_id, args, kwargs, einfo)

        for _fn, _args in self._fns_after_return:
            _ = _fn(*_args) if _args else _fn()
        self._fns_after_return = []

    def add_fn_after_return(self, fn, *args):
        self._fns_after_return.append((fn, args))
