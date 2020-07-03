import os
from time import sleep
import msgpack
from nonblock import bgread
from scenegraph import scenegraph

class Messenger:
	messages_in = 0
	messages_out = 0
	scenegraph = None

	pending_messages = []

	check_for_messages_enabled = True
	check_for_messages_thread = None

	message_type_verification = [
		[int, int, str],
		[int, int, str, str, list],
		[int, int, None]
	]

	message_types = {}

	message_queue = None

	def __init__(self, messages_in, messages_out, scenegraph):
		self.messages_in = messages_in
		self.messages_out = messages_out
		self.scenegraph = scenegraph

		self.message_types[0] = self.handle_message_error
		self.message_types[1] = self.handle_message_method_call
		self.message_types[2] = self.handle_message_method_return
		self.message_types[3] = self.handle_message_signal

		self.message_queue = bgread(messages_in)

	def generate_message_id(self):
		i = 0
		while i in [item[1] for item in self.pending_messages]:
			i += 1
		return i

	def get_message(self, id):
		id_list = [item[1] for item in self.pending_messages]

		if id not in id_list:
			return None

		message = self.pending_messages[id_list.index(id)]
		print(message)
		return message

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
			self.send_message([2, message[1], method_return])
		else:
			self.send_message([0, message[1], error])

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

	def send_message(self, message, verification = False):
		if verification:
			message_type = message[0]
			message_type_verification_types = self.message_type_verification[message_type]

			if len(message) is not len(message_type_verification_types):
				print("Length of",message,"is incorrect")
				return None
			for i in range(len(message)):
				if type(message[i]) is not message_type_verification_types[i]:
					print("Argument types of",message,"are incorrect")
					return None

		print("Sending message", message)
		binary_message = msgpack.packb(message)
		binary_message_length = len(binary_message).to_bytes(16, byteorder='big', signed=False)
		os.write(self.messages_out, binary_message_length)
		os.write(self.messages_out, binary_message)

	def execute_remote_method(self, object_path, method_name, method_args, async_function=None):
		message = [1, self.generate_message_id(), object_path, method_name, method_args]
		if async_function is not None:
			message.append(async_function)
		self.pending_messages.append(message)
		self.send_message(message)

		if async_function is None:
			index = self.pending_messages.index(message)
			while self.pending_messages[index] != 2:
				sleep(0.0001)
			return_message = self.pending_messages[index]
			self.pending_messages.pop(index)
			return return_message[2]

	def send_signal(self, object_path, signal_name, signal_data):
		message = [3, object_path, signal_name, signal_data]
		self.send_message(message)
