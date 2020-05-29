from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from neonotes.mapped_classes import *
import os

DB_PATH = 'tagger.db'




def is_db():
	if os.path.isfile(DB_PATH):
		return True
	else:
		return False


def connect_database(path=DB_PATH):
	path = 'sqlite:///{}'.format(path)
	engine = create_engine(path, echo=False)
	# Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)
	return engine

def new_database(path=DB_PATH):
	path = 'sqlite:///{}'.format(path)
	engine = create_engine(path, echo=False)
	Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)
	return engine

def start_db(path=DB_PATH):
	''''returns Session object'''
	if is_db():

		engine = connect_database(path)
		Session = sessionmaker(bind=engine)
		return Session

	else:
		print('no database found, creating database...')
		engine = new_database(path)
		Session = sessionmaker(bind=engine)
		return Session


Session = scoped_session(start_db(DB_PATH ))

# if __name__ == '__main__':
