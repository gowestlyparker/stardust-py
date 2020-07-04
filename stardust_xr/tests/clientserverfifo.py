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

s2c_path = "/tmp/s2c"
c2s_path = "/tmp/c2s"

def main():
	if not os.path.exists(s2c_path):
		os.mkfifo(s2c_path)
	if not os.path.exists(c2s_path):
		os.mkfifo(c2s_path)

	if os.fork() != 0:
		server()
	else:
		client()

def client():
	s2c_read = os.open(s2c_path, os.O_RDONLY | os.O_NONBLOCK)
	c2s_write = os.open(c2s_path, os.O_WRONLY)

	client_graph = stardust_xr.Scenegraph({})
	client_messager = stardust_xr.Messenger(s2c_read, c2s_write, client_graph)
	print("Client messager started")

	client_messager.execute_remote_method("/res/obj", "new", ["/obj/cubedemo/cube", "~/Downloads/cube.gltf"])

	# message_test = [1, client_messager.generate_message_id(), "/res/obj", "new", ["/obj/cubedemo/cube", "~/Downloads/cube.gltf"]]
	# client_messager.send_message(message_test, verification=True)

def server():
	c2s_read = os.open(c2s_path, os.O_RDONLY | os.O_NONBLOCK)
	s2c_write = os.open(s2c_path, os.O_WRONLY)

	server_graph = stardust_xr.Scenegraph({})

	obj_test = test_message_object()
	server_graph.new_object("/res/obj", obj_test, {"new": obj_test.new})


	server_messager = stardust_xr.Messenger(c2s_read, s2c_write, server_graph)
	print("Server messager started")

if __name__ == "__main__":
	main()
