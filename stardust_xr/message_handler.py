import os
import msgpack
import threading
import time
from . import message_producer, scenegraph, utils

class MessageHandler (threading.Thread):
	messages_in = 0
	pending_messages = None
	scenegraph = None

	message_producer = None

	message_types = {}

	def __init__(self, messages_in, pending_messages, scenegraph, message_producer):
		threading.Thread.__init__(self)
		self.message_producer = message_producer

		self.messages_in = messages_in
		self.pending_messages = pending_messages
		self.scenegraph = scenegraph

		self.message_types[0] = self.handle_message_error
		self.message_types[1] = self.handle_message_method_call
		self.message_types[2] = self.handle_message_method_return
		self.message_types[3] = self.handle_message_signal

	def run(self):
		while True:
			if not self.process_messages():
				break

	def get_message(self, id):
		id_list = [item[1] for item in self.pending_messages]

		if id not in id_list:
			return None

		message = self.pending_messages[id_list.index(id)]
		return message

	@utils.benchmark
	def process_messages(self):
		binary_message_length = os.read(self.messages_in, 16)
		message_length = int.from_bytes(binary_message_length, byteorder='big', signed=False)
		if message_length == 0:
			print("Pipe's write on other end broke")
			return False

		print("Recieved message of length", message_length)

		binary_message = os.read(self.messages_in, message_length)
		message = msgpack.unpackb(binary_message)

		print("with content", message)
		self.message_types[message[0]](message)
		return True

	def handle_message_error(self, message):
		print(message[2])

	def handle_message_method_call(self, message):
		method_return, error = self.scenegraph.call_object_method(message[2], message[3], message[4])
		if error is None:
			self.message_producer.send_message([2, message[1], method_return])
		else:
			self.message_producer.send_message([0, message[1], error])

	def handle_message_method_return(self, message):
		pending_message = self.get_message(message[1])
		if pending_message is None:
			return None

		if len(pending_message) == 5:
			self.pending_messages[message[1]] = message
		elif len(pending_message) == 6:
			pending_message[5](pending_message[2])
			self.pending_messages.remove(pending_message)

	def handle_message_signal(self, message):
		pass
