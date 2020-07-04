import os
import msgpack

class MessageProducer:
	messages_out = 0
	pending_messages = None
	scenegraph = None

	def __init__(self, messages_out, pending_messages, scenegraph):
		self.messages_out = messages_out
		self.pending_messages = pending_messages
		self.scenegraph = scenegraph

	def send_message(self, message):
		binary_message = msgpack.packb(message)
		binary_message_length = len(binary_message).to_bytes(16, byteorder='big', signed=False)
		os.write(self.messages_out, binary_message_length)
		os.write(self.messages_out, binary_message)

	def send_signal(self, object_path, signal_name, signal_data):
		message = [3, object_path, signal_name, signal_data]
		self.send_message(message)
