import os
import msgpack
from . import scenegraph

class MessageHandler:
	messages_in = 0
	pending_messages = None
	scenegraph = None

	check_for_messages_enabled = True
	check_for_messages_thread = None

	message_types = {}

	def __init__(self, messages_in, pending_messages, scenegraph):
		self.messages_in = messages_in
		self.pending_messages = pending_messages
		self.scenegraph = scenegraph

		self.message_types = {
			self.handle_message_error,
			self.handle_message_method_call,
			self.handle_message_method_return,
			self.handle_message_signal
		}

	def process_messages(self):
		binary_message_length = os.read(self.messages_in, 16)
		message_length = int.from_bytes(binary_message_length, byteorder='big', signed=False)
		binary_message = os.read(self.messages_in, message_length)
		message = msgpack.unpackb(binary_message)

		print("Recieved message", message, "of length", message_length)
		self.message_types[message[0]](message)

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
			pending_message = message
		elif len(pending_message) == 6:
			pending_message[5](pending_message[2])
			self.pending_messages.remove(pending_message)

	def handle_message_signal(self, message):
		pass
