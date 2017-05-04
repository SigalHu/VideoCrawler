from zipfile import *
import os
from print_manager import *

# hu 压缩成zip文件
def zip_file(file_path, zip_name):
	zip_id = None
	try:
		if os.path.isdir(file_path):
			if zip_name[-4:].lower() != '.zip':
				zip_name += '.zip'
			zip_name = os.path.abspath(zip_name)

			zip_id = ZipFile(zip_name, 'w', ZIP_DEFLATED)
			for root, dirs, files in os.walk(file_path):
				for directory in dirs:
					zip_id.write(os.path.join(root, directory))
				for file in files:
					zip_id.write(os.path.join(root, file))
		else:
			zip_id = ZipFile(zip_name, 'w', ZIP_DEFLATED)
			zip_id.write(file_path)
	except Exception as ex:
		show_error('压缩文件失败！\n%s' % ex)
		return False
	else:
		show_emphasize('压缩文件成功！\n压缩文件路径：%s' % zip_name)
		return True
	finally:
		if zip_id is not None:
			zip_id.close()

# hu 解压zip文件
def unzip_file(zip_name):
	zip_id = None
	try:
		zip_id = ZipFile(zip_name)
		for file in zip_id.namelist():
			zip_id.extract(file,r'.')
	except Exception as ex:
		show_error('解压缩文件失败！\n%s' % ex)
	else:
		path = os.path.abspath(zip_name)
		show_emphasize('解压缩文件成功！\n文件路径：%s' % path[:-len(zip_name)])
	finally:
		if zip_id is not None:
			zip_id.close()

def __main():
	# zip_file('files/a','a.zip')
	unzip_file('a.zip')

if __name__ == '__main__':
	__main()
