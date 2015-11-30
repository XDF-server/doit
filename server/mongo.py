# *-* coding:utf-8 *-*

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure,ServerSelectionTimeoutError
from base import Configer
from exception import DBException

class Mongo(object):

	def __init__(self):

		self.client = None	
		self.db = None
		self.collection = None

	def connect(self,db):
	
		configer = Configer()

		mongo_host = configer.get_configer('MONGO','host')
		mongo_port = int(configer.get_configer('MONGO','port'))
		mongo_timeout = int(configer.get_configer('MONGO','timeout'))
			
		try:
			self.client = MongoClient(host = mongo_host,port = mongo_port,connectTimeoutMS = mongo_timeout)
			self.db = self.client[db]
	
		except ConnectionFailure,e:
			LOG.error('mongo connect failed [%s]' % e)
			raise DBException('mongo connect failed')

	def select_collection(self,collection):
		
		try:
			self.collection = self.db[collection]

		except ServerSelectionTimeoutError as e:
			LOG.error('mongo select failed [%s]' % e)
			raise DBException('mongo select failed')
		
	def insert_one(self,data):
		
		return self.collection.insert_one(data).inserted_id

	def insert(self,data):
		
		return self.collection.insert_one(data)
		
	def get_collection(self):
			
		return self.collection

	def find_one(self,*args,**kwargs):
		return self.collection.find_one(*args,**kwargs)
		
	def update_many(self,filter,update):
		return self.collection.update_many(filter,update).modified_count

        def get_handle(self):
                return MongoClient(host = Configer().get_configer('MONGO', 'host'), port = int(Configer().get_configer('MONGO', 'port')))

        def remove(self, data):
            return self.collection.remove(data)









