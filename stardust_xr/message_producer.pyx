import os
import msgpack
import flatbuffers
from . import message, utils

cdef class MessageProducer:
	cdef int messages_out
	cdef list pending_messages
	scenegraph = None

	flat_builder = None

	def __init__(self, int messages_out, list pending_messages, scenegraph):
		self.messages_out = messages_out
		self.pending_messages = pending_messages
		self.scenegraph = scenegraph

		self.flat_builder = flatbuffers.Builder(1024)

	cdef send_message(self, list message):
		print("Sending message",message)
		binary_message = self.encode_message(message)
		binary_message_length = len(binary_message).to_bytes(16, byteorder='big', signed=False)
		os.write(self.messages_out, binary_message_length)
		os.write(self.messages_out, binary_message)

	cdef encode_message(self, list message_tuple):
		object_string = None
		method_string = None
		error_string = None

		packed_data = None

		if message_tuple[0] in [1, 3]: #If the message is method call or signal attach an object name and method
			object_string = self.flat_builder.CreateString(message_tuple[2])
			method_string = self.flat_builder.CreateString(message_tuple[3])
			packed_data = msgpack.packb(message_tuple[4])
		elif message_tuple[0] == 0:
			error_string = self.flat_builder.CreateString(message_tuple[2])
		else:
			packed_data = msgpack.packb(message_tuple[2])

		if message_tuple[0] != 0:
			flat_data = self.flat_builder.CreateByteVector(packed_data)

		message.MessageStart(self.flat_builder)
		message.MessageAddType(self.flat_builder, message_tuple[0])
		message.MessageAddId(self.flat_builder, message_tuple[1])

		if message_tuple[0] in [1, 3]: #If the message is method call or signal attach an object name and method
			message.MessageAddObject(self.flat_builder, object_string)
			message.MessageAddMethod(self.flat_builder, method_string)

		if message_tuple[0] != 0:
			message.MessageAddData(self.flat_builder, flat_data)
		self.flat_builder.Finish(message.MessageEnd(self.flat_builder))

		return self.flat_builder.Output()


	cdef send_signal(self, char *object_path, char *signal_name, list signal_data):
		message = [3, object_path, signal_name, signal_data]
		self.send_message(message)
