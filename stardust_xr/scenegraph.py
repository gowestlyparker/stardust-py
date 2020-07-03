#!/usr/bin/env python3
class Scenegraph:
	heirarchy = {}

	def __init__(self, init_heirarchy):
		self.heirarchy = init_heirarchy

	# Override this method to integrate into an existing scenegraph
	def get_object(self, path_string):
		path_tuple = path_string[1:].split('/')
		#THIS is bugging out -- moses @ jun 9, 11 AM
		current_object = self.heirarchy
		for tuple_item in path_tuple:
			print("current object is " , current_object, "current tuple_item is " , tuple_item)
			if type(current_object) is dict:
				if tuple_item in current_object:
					current_object = current_object[tuple_item]
				else:
					print("Path", path_tuple, "does not exist")
					return None
			else:
				print("Path", path_tuple, "is not a dict")
				return None

		return current_object

	def new_object(self, path_tuple, object_reference, object_methods):
		current_object = self.heirarchy
		for tuple_item in path_tuple:
			if tuple_item not in current_object:
				current_object[tuple_item] = {}
			elif "object_reference" in current_object:
				print(tuple_item, "is an object")
				return None
			current_object = current_object[tuple_item]

		current_object["object_reference"] = object_reference
		current_object["object_methods"] = object_methods
		print("Heirarchy is now ", self.heirarchy)
		return current_object

	def del_object(self, path_tuple, delete_reference = True):
		object = self.get_object(path_tuple)
		if delete_reference:
			del object["object_reference"]
		del object

	# Override this method to integrate into an existing scenegraph
	def call_object_method(self, path_tuple, method_name, args):
		object_methods = self.get_object(path_tuple)["object_methods"]
		if method_name not in object_methods:
			error = method_name+" is not in "+path_tuple[-1]+"'s methods"
			return None, error
		return object_methods[method_name](*args), None
