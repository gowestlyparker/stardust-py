from setuptools import setup, Extension
from Cython.Build import cythonize

ext_modules = cythonize([
	Extension("stardust_xr.message", ["stardust_xr/message.pyx"]),
	Extension("stardust_xr.messenger", ["stardust_xr/messenger.pyx"]),
	Extension("stardust_xr.message_producer", ["stardust_xr/message_producer.pyx"]),
	Extension("stardust_xr.message_handler", ["stardust_xr/message_handler.pyx"]),
	Extension("stardust_xr.scenegraph", ["stardust_xr/scenegraph.pyx"]),
	Extension("stardust_xr.utils", ["stardust_xr/utils.pyx"]),
], compiler_directives={'language_level' : "3"})

setup(
	name='stardust_xr',
	version='0.1',
	description='Python module for Stardust clients and server implementations',
	url='https://github.com/technobaboo/stardust-py',
	author='Nova King',
	author_email='technobaboo@gmail.com',
	license='MIT',
#	packages=['stardust_xr'],
	ext_modules = ext_modules,
	zip_safe=False
)
