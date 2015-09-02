# *-* coding:utf-8 *-*

from loader import Loader

if __name__ == '__main__':

	Loader.load()

	from gl import LOG

	LOG.info('START[doit start]')

	Loader.start()
