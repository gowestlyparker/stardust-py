import os
import flatbuffers
import flatbuffers.flexbuffers as flexbuffers
from . import message, utils

class MessageProducer:
	messages_out = 0
	pending_messages = None
	scenegraph = None

	flat_builder = None
	flex_builder = None

	def __init__(self, messages_out, pending_messages, scenegraph):
		self.messages_out = messages_out
		self.pending_messages = pending_messages
		self.scenegraph = scenegraph

		self.flat_builder = flatbuffers.Builder(1024)
		self.flex_builder = flexbuffers.Builder()

	def send_message(self, message):
		print("Sending message",message)
		binary_message = self.encode_message(message)
		binary_message_length = len(binary_message).to_bytes(16, byteorder='big', signed=False)
		os.write(self.messages_out, binary_message_length)
		os.write(self.messages_out, binary_message)

	def encode_message(self, message_tuple):
		self.flex_builder.Clear()

		object_string = None
		method_string = None
		blank_string = None

		if message_tuple[0] in [1, 3]: #If the message is method call or signal attach an object name and method
			object_string = self.flat_builder.CreateString(message_tuple[2])
			method_string = self.flat_builder.CreateString(message_tuple[3])
			self.flex_builder.Add(message_tuple[4])
		else:
			blank_string = self.flat_builder.CreateString("")
		if message_tuple[0] == 0:
			self.flex_builder.String(message_tuple[2])
		if message_tuple[0] == 2:
			self.flex_builder.Add(message_tuple[2])

		packed_data = self.flex_builder.Finish()
		flat_data = self.flat_builder.CreateByteVector(packed_data)

		message.MessageStart(self.flat_builder)
		message.MessageAddType(self.flat_builder, message_tuple[0])
		message.MessageAddId(self.flat_builder, message_tuple[1])

		if message_tuple[0] in [1, 3]: #If the message is method call or signal attach an object name and method
			message.MessageAddObject(self.flat_builder, object_string)
			message.MessageAddMethod(self.flat_builder, method_string)
		else: #If the message is error or method return no need to attach object or method
			message.MessageAddObject(self.flat_builder, blank_string)
			message.MessageAddMethod(self.flat_builder, blank_string)

		message.MessageAddData(self.flat_builder, flat_data)
		self.flat_builder.Finish(message.MessageEnd(self.flat_builder))

		return self.flat_builder.Output()


	def send_signal(self, object_path, signal_name, signal_data):
		message = [3, object_path, signal_name, signal_data]
		self.send_message(message)
