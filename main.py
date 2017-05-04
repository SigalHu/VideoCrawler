import platform
import os
import asyncio
import num_item
import dir_helper
import zip_file
import time
from num_searcher import search_and_save

def __main():
	path = 'files'
	cfg_file = 'num_searcher.cfg'

	phantomJS_path = None
	if platform.platform().lower().startswith('windows'):
		phantomJS_path = r'D:/phantomjs/bin/phantomjs.exe'
	elif platform.platform().lower().startswith('linux'):
		phantomJS_path = r'/home/download/phantomjs/bin/phantomjs'
	else:
		print('不支持%s' % platform.platform())
		exit(0)

	if not os.path.exists(path):
		os.mkdir(path)

	loop = asyncio.get_event_loop()
	search_item = num_item.get_search_item(cfg_file)
	while search_item:
		save_path = search_and_save(phantomJS_path, search_item, loop, path)
		if save_path:
			if platform.platform().lower().startswith('linux'):
				if zip_file.zip_file(save_path, save_path + '.zip'):
					dir_helper.remove_all_files(save_path)
			num_item.set_search_item(cfg_file, search_item)
			search_item = num_item.get_search_item(cfg_file)
		else:
			time.sleep(10)
	loop.close()


if __name__ == '__main__':
	__main()