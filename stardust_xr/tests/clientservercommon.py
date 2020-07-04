import time
import stardust_xr

class test_message_object:
	def __init__(self):
		pass

	def time(self):
		print("Time method called at time",time.time())
		return time.time()

def client(s2c_read, c2s_write):
	client_graph = stardust_xr.Scenegraph({})
	client_messager = stardust_xr.Messenger(s2c_read, c2s_write, client_graph)
	print("Client messager started")

	start_time = time.time()
	message_time = client_messager.execute_remote_method("/test", "time")
	return_time = time.time()

	print("The message took",message_time - start_time, "seconds to execute the remote method and",return_time - message_time,"seconds to get back, taking",return_time - start_time,"seconds blocked")
	print("Press enter to exit")

def server(c2s_read, s2c_write):
	server_graph = stardust_xr.Scenegraph({})

	obj_test = test_message_object()
	server_graph.new_object("/test", obj_test, {"time": obj_test.time})

	server_messager = stardust_xr.Messenger(c2s_read, s2c_write, server_graph)
	print("Server messager started")
	input("")
