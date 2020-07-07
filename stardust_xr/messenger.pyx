import os
from time import sleep
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
		return len(self.pending_messages)

	def execute_remote_method(self, object_path, method_name, method_args = None, async_function=None):
		id = self.generate_message_id()
		message = [1, id, object_path, method_name, method_args]
		if async_function is not None:
			message.append(async_function)

		self.pending_messages.append(message)
		self.message_producer.send_message(message)

		if async_function is None:
			while self.pending_messages[id][0] != 2:
				sleep(0.00000001)
			return_message = self.pending_messages[id]
			self.pending_messages.pop(id)
			return return_message[2]
