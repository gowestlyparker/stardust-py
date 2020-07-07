import time

def benchmark(func):
	def wrapper(*arg):
		t = time.time()
		res = func(*arg)
		print("Function took",(time.time()-t),"seconds to run")
		return res

	return wrapper
