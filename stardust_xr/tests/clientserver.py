#!/usr/bin/env python3
import os
import msgpack
import time
import stardust_xr

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
		server(c2s_read, s2c_write)
	else:
		os.close(s2c_write)
		os.close(c2s_read)
		client(s2c_read, c2s_write)

def client(s2c_read, c2s_write):
	client_graph = stardust_xr.Scenegraph({})
	client_messager = stardust_xr.Messenger(s2c_read, c2s_write, client_graph)
	print("Client messager started")

	print(time.time())
	client_messager.execute_remote_method("/res/obj", "new", ["/obj/cubedemo/cube", "~/Downloads/cube.gltf"])

	# message_test = [1, client_messager.generate_message_id(), "/res/obj", "new", ["/obj/cubedemo/cube", "~/Downloads/cube.gltf"]]
	# client_messager.send_message(message_test, verification=True)

def server(c2s_read, s2c_write):
	server_graph = stardust_xr.Scenegraph({})

	obj_test = test_message_object()
	print(server_graph.new_object(server_graph.format_path("/res/obj"), obj_test, {"new": obj_test.new}))


	server_messager = stardust_xr.Messager(c2s_read, s2c_write, server_graph)
	print("Server messager started")

if __name__ == "__main__":
	main()
