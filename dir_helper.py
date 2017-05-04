import os
import re
from print_manager import *


def get_valid_name(expected_file_name, instead_str=' '):
	try:
		valid_name = re.compile(r'[/\\:*?"<>|]').sub(instead_str, expected_file_name)
	except Exception as ex:
		show_error('%s：%s' % (get_valid_name.__name__, ex))
	else:
		return valid_name.strip(' ')


def rename_ansi_name(file_name):
	try:
		if os.path.exists(file_name):
			path, name = os.path.split(file_name)
			new_name = name.encode(encoding='ansi').decode('utf-8')
			file_new_name = os.path.join(path, new_name)
			os.rename(file_name, file_new_name)
			return file_new_name
		else:
			show_error('%s不存在！' % file_name)
	except Exception as ex:
		show_error('文件%s重命名失败！\n%s：%s' % (file_name, rename_ansi_name.__name__, ex))


def rename_all_ansi_name(dir_path):
	if os.path.isdir(dir_path):
		dir_list = [dir_path]
		# 修改文件名
		for root, dirs, files in os.walk(dir_path):
			for directory in dirs:
				dir_list.append(os.path.join(root, directory))
			for file in files:
				rename_ansi_name(os.path.join(root, file))
		# 修改文件夹名
		while len(dir_list):
			rename_ansi_name(dir_list.pop())
		return True
	else:
		show_error('%s不存在！' % dir_path)
		return False

def remove_all_files(path):
	try:
		if os.path.isdir(path):
			dir_list = []
			# 删除文件
			for root, dirs, files in os.walk(path):
				for directory in dirs:
					dir_list.append(os.path.join(root, directory))
				for file in files:
					os.remove(os.path.join(root, file))
			# 删除文件夹
			while len(dir_list):
				os.removedirs(dir_list.pop())
			os.removedirs(path)
		else:
			os.remove(path)
	except Exception as ex:
		show_error('%s：%s' % (remove_all_files.__name__, ex))
		return False
	else:
		show_emphasize('删除%s成功！' % path)
		return True


def __main():
	dir_name = '文件夹'
	path = 'files'
	path = os.path.join(path, dir_name)
	# remove_all_files(path)


if __name__ == '__main__':
	__main()
