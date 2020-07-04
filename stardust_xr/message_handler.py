import os
import threading
import time
import msgpack
import flatbuffers
from . import message, message_producer, scenegraph, utils

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

	def decode_data(self, flat_message):
		flex_bytes = flat_message.DataAsNumpy().tobytes()
		data = msgpack.unpackb(flex_bytes)
		return data

	def process_messages(self):
		binary_message_length = os.read(self.messages_in, 16)
		message_length = int.from_bytes(binary_message_length, byteorder='big', signed=False)
		if message_length == 0:
			print("Pipe's write on other end broke")
			return False

		binary_message = os.read(self.messages_in, message_length)
		flat_message = message.Message.GetRootAsMessage(binary_message, 0)

		self.message_types[flat_message.Type()](flat_message)
		return True

	def handle_message_error(self, flat_message):
		print(flat_message.Error().decode('ascii'))

	def handle_message_method_call(self, flat_message):
		method_return, error = self.handle_message_signal(flat_message)
		if error is None:
			self.message_producer.send_message([2, flat_message.Id(), method_return])

	def handle_message_method_return(self, flat_message):
		pending_message = self.pending_messages[flat_message.Id()]
		#if pending_message is None:
		#	return None

		if len(pending_message) == 5:
			pending_message[0] = 2
			pending_message[2] = self.decode_data(flat_message)
		elif len(pending_message) == 6:
			pending_message[5](pending_message[2])
			self.pending_messages.remove(pending_message)

	def handle_message_signal(self, flat_message):
		method_return, error = self.scenegraph.call_object_method(flat_message.Object().decode('ascii'), flat_message.Method().decode('ascii'), self.decode_data(flat_message))

		if error is not None:
			self.message_producer.send_message([0, flat_message.Id(), error])
		return method_return, error
