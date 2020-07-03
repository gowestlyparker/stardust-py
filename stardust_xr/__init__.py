from . import messenger, scenegraph

def Messenger(messages_in, messages_out, scenegraph):
	return messenger.Messenger(messages_in, messages_out, scenegraph)

def Scenegraph(init_heirarchy):
	return scenegraph.Scenegraph(init_heirarchy)
