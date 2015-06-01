"""
This is just a slightly abbreviated version of the sqlalchemy ORM tutorial:
http://docs.sqlalchemy.org/en/rel_1_0/orm/tutorial.html
"""


############### CONNECTING ####################
# connects to an in-memory-only SQLite database
# create_engine() returns an instance of Engine, the core interface to the database
# echo flag logs all generated SQL produced
from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:', echo=True)
# when using the ORM, we typically don't use the Engine directly once created
# instead, it's used behind the scenes by the ORM
# Examples of Database Urls: http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html#database-urls


############### DECLARE A MAPPING ####################
# the configuration process starts by describing the database tables, and then
# defining our own classes which will be mapped to those tables
# classes mapped are defined in terms of a **declarative base class**

# create the base class
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


# define tables and the Classes which map to them
# class needs a __tablename__ and at least one Column which is part of a primary key
from sqlalchemy import Column, Integer, String
class User(Base):
	__tablename__= 'users'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	fullname = Column(String)
	password = Column(String)

	# this is optional
	def __repr__(self):
		return "<User(name='%s', fullname='%s', password='%s')>" % (self.name, self.fullname, self.password)



############### CREATE A SCHEMA ####################
# Declarative Base makes a table using the User class declaration
# to see this object by calling User.__table__

# The Table object is a member of a larger collection known as MetaData. 
# When using Declarative, this object is available using the .metadata attribute 
# of our declarative base class.

# As our SQLite database does not actually have a users table present, 
# we can use MetaData to issue CREATE TABLE statements to the database for 
# all tables that don’t yet exist. 
# Below, we call the MetaData.create_all() method, passing in our Engine as a source of database connectivity:
Base.metadata.create_all(engine)




####### CREATE AN INSTANCE OF THE MAPPED CLASS ########
ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')



############### CREATING A SESSION ####################
# now we are ready to start talking to the database
# the ORM's 'handle' to the database is the Session

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
# This custom-made Session class will create new Session objects 
# which are bound to our database.

# whenever you need to have a conversation with the database, 
# you instantiate a Session:
session = Session()
# The above Session is associated with our SQLite-enabled Engine, 
# but it hasn’t opened any connections yet. When it’s first used, 
# it retrieves a connection from a pool of connections maintained 
# by the Engine, and holds onto it until we commit all changes and/or 
# close the session object.



############### Adding New Objects ####################
# To persist our User object, we add() it to our Session:
session.add(ed_user)
# at this point, we say that the instance is **pending**
# no SQL has yet been issued and the object is not yet represented 
# by a row in the database

# The Session will issue the SQL to persist Ed Jones as soon as is needed, 
# using a process known as a **flush**.

# If we query the database for Ed Jones, all pending information will 
# first be flushed, and the query is issued immediately thereafter.
our_user = session.query(User).filter_by(name='ed').first()
# our_user = <User(name='ed', fullname='Ed Jones', password='edspassword')>

# we can add more User objects at once using add_all():
session.add_all([
	User(name='wendy', fullname='Wendy Williams', password='foobar'),
	User(name='mary', fullname='Mary Contrary', password='xxg527'),
	User(name='fred', fullname='Fred Flinstone', password='blah')])

# issue all remaining changes to the database and commit the transaction
session.commit()
# commit() flushes whatever remaining changes remain to the database,
# and commits the transaction





