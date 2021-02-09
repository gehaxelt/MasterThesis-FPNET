import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy import func
from sqlalchemy.sql import text
from sqlalchemy.event import listen
import os
import sys

LOGPATH = sys.argv[1]

def load_extension(dbapi_conn, unused):
    dbapi_conn.enable_load_extension(True)
    dbapi_conn.load_extension(os.path.abspath(os.path.dirname(sys.argv[0])) + os.sep + 'extension-functions')

sql_engine = create_engine('sqlite:///' + os.path.abspath(LOGPATH + os.sep + 'scores.db'), echo=False)
listen(sql_engine, 'connect', load_extension)

sql_session_maker = sessionmaker(bind=sql_engine)
sql_session = sql_session_maker()
sql_base = declarative_base()

score_cat_association_table = Table('score_cat_association', sql_base.metadata,
    Column('score_id', Integer, ForeignKey('fpscores.id')),
    Column('cat_id', Integer, ForeignKey('fpcategories.id'))
)
score_scriptorigin_association_table = Table('score_scriptorigin_association', sql_base.metadata,
    Column('score_id', Integer, ForeignKey('fpscores.id')),
    Column('scriptorigin_id', Integer, ForeignKey('fpscriptorigins.id'))
)
scriptorigin_scriptfunctioncall_association_table = Table('scriptorigin_scriptfunctioncall_association', sql_base.metadata,
    Column('scriptorigin_id', Integer, ForeignKey('fpscriptorigins.id')),
    Column('scriptfunctioncall_id', Integer, ForeignKey('fpscriptfunctioncalls.id'))
)

class FPScriptFunctionCall(sql_base):
    __tablename__ = 'fpscriptfunctioncalls'

    id = Column(Integer, primary_key=True)
    idx = Column(Integer)
    gidx = Column(Integer)
    functioncall = Column(String)
    obj = Column(String)
    category_id = Column(Integer, ForeignKey('fpcategories.id'))
    category = relationship("FPCategory", backref='scriptfunctioncalls')


class FPScriptOrigin(sql_base):
    __tablename__ = 'fpscriptorigins'

    id = Column(Integer, primary_key=True)
    idx = Column(Integer)
    url = Column(String)
    proto = Column(String)
    subdomain = Column(String)
    domain = Column(String) #fld in reality (google.de)
    domain2 = Column(String) # domain (google)
    tld = Column(String)
    path = Column(String)
    filename = Column(String)
    score = Column(Integer)

    function_calls = relationship("FPScriptFunctionCall", secondary=scriptorigin_scriptfunctioncall_association_table, backref='fpscriptorigin')


class FPScore(sql_base):
    __tablename__ = 'fpscores'

    id = Column(Integer, primary_key=True)
    trace_id = Column(String)
    subdomain = Column(String)
    domain = Column(String) #fld in reality (google.de)
    domain2 = Column(String) # domain (google)
    tld  = Column(String)
    date = Column(Integer)
    loadtime = Column(Integer)
    score = Column(Integer)
    coverage_entities = Column(String)
    coverage_categories = Column(String)
    aggressive_coverage = Column(String)
    aggressive_categories = Column(String)
    script_origins_calls_cnt = Column(Integer)

    categories = relationship("FPCategory", secondary=score_cat_association_table, backref='fpscores')
    script_origins = relationship("FPScriptOrigin", secondary=score_scriptorigin_association_table, backref='fpscores')

class FPCategory(sql_base):
    __tablename__ = 'fpcategories'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    aggro = Column(Boolean)

sql_base.metadata.create_all(sql_engine)
