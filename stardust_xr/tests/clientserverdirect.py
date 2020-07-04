#!/usr/bin/env python3
import os
import clientservercommon

class test_message_object:
	def __init__(self):
		pass

	def new(self, res_path, file_path):
		print("New method called with parameters",res_path,"and",file_path,"at time",time.time())

def main():
	c2s_read, c2s_write = os.pipe()
	s2c_read, s2c_write = os.pipe()

	if os.fork() != 0:
		os.close(s2c_read)
		os.close(c2s_write)
		clientservercommon.server(c2s_read, s2c_write)
	else:
		os.close(s2c_write)
		os.close(c2s_read)
		clientservercommon.client(s2c_read, c2s_write)

if __name__ == "__main__":
	main()
