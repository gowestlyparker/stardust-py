#!/usr/bin/env python3
import os
import clientservercommon

s2c_path = "/tmp/s2c"
c2s_path = "/tmp/c2s"

def main():
	if not os.path.exists(s2c_path):
		os.mkfifo(s2c_path)
	if not os.path.exists(c2s_path):
		os.mkfifo(c2s_path)

	if os.fork() != 0:
		read = os.open(c2s_path, os.O_RDONLY)
		write = os.open(s2c_path, os.O_WRONLY)
		#os.write(s2c_write, b"server")
		clientservercommon.server(read, write)
	else:
		write = os.open(c2s_path, os.O_WRONLY)
		os.write(write, b"")
		read = os.open(s2c_path, os.O_RDONLY)
		clientservercommon.client(read, write)

if __name__ == "__main__":
	main()
