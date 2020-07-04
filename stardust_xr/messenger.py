import os
from time import sleep
import msgpack
from . import message_producer, message_handler, scenegraph

class Messenger:
	message_producer = None
	message_handler = None
	scenegraph = None

	pending_messages = []

	def __init__(self, messages_in, messages_out, scenegraph):
		self.message_producer = message_producer.MessageProducer(messages_out, self.pending_messages, scenegraph)
		self.message_handler = message_handler.MessageHandler(messages_in, self.pending_messages, scenegraph, self.message_producer)
		self.scenegraph = scenegraph

		self.message_handler.daemon = True
		self.message_handler.start()

	def generate_message_id(self):
		i = 0
		while i in [item[1] for item in self.pending_messages]:
			i += 1
		return i

	def execute_remote_method(self, object_path, method_name, method_args = [], async_function=None):
		message = [1, self.generate_message_id(), object_path, method_name, method_args]
		if async_function is not None:
			message.append(async_function)

		index = len(self.pending_messages)
		self.pending_messages.append(message)
		self.message_producer.send_message(message)

		if async_function is None:
			print("Pending messages:",self.pending_messages)
			while self.pending_messages[index][0] != 2:
				sleep(0.00000001)
			return_message = self.pending_messages[index]
			self.pending_messages.pop(index)
			print("Message",message,"returned",return_message)
			return return_message[2]
