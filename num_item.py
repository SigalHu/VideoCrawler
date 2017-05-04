from xml.dom.minidom import parse
import xml.dom.minidom
from print_manager import *
import os
import re
from enum import Enum

class ItemStatus(Enum):
	IN_SEARCH = 0
	NO_SEARCH = 1
	SEARCH_DONE = 2


def get_search_item(path, is_urgent=False):
	"""
	功能：从指定文件获取一个搜索关键字

	:param path: 配置文件路径
	:param is_urgent: True--从'搜索中'中获取一个搜索关键字，若其中为空，则在'未搜索'中获取，
		并将获取的关键字移动到'搜索中'；False--从'搜索中'中获取一个搜索关键字，若其中为空，则返回None
	:return: 默认返回搜索关键字，若'搜索中'和'未搜索'都为空则返回None
	"""
	search_item = None
	try:
		DOMTree = xml.dom.minidom.parse(path)
		search_status = DOMTree.documentElement

		search_doing = search_status.getElementsByTagName('搜索中')[0]
		key_word = search_doing.getElementsByTagName('关键词')
		if key_word:
			search_item = key_word[0].childNodes[0].data
			return search_item

		if is_urgent:
			search_donot = search_status.getElementsByTagName('未搜索')[0]
			key_words = search_donot.getElementsByTagName('关键词')
			if key_words:
				search_item = key_words[0].childNodes[0].data
				search_donot.removeChild(key_words[0])
				search_doing.appendChild(key_words[0])

				xml_str = DOMTree.toprettyxml(indent='\t', newl='\n', encoding='utf-8').decode('utf-8')
				xml_compile = re.compile(r'\n[\n\t\s]+\n')
				xml_str = xml_compile.sub('\n', xml_str)
				with open(path + '.tmp', 'w', encoding='utf-8') as fid:
					fid.write(xml_str)

				os.remove(path)
				os.rename(path + '.tmp', path)
	except Exception as ex:
		if os.path.exists(path + '.tmp'):
			os.remove(path + '.tmp')
		show_warning('获取关键词失败！\n%s：%s' % (get_search_item.__name__, ex))
	finally:
		return search_item


def set_search_item(path, search_item, item_status=ItemStatus.SEARCH_DONE, ignore_case=False):
	"""
	功能：将指定文件中的搜索关键字移动到指定位置
	:param path: 配置文件路径
	:param search_item: 搜索关键字
	:param item_status: 目标位置('搜索中','未搜索','已搜索'）
	:param ignore_case: 是否忽略大小写
	:return: 成功则返回True，搜索关键字在文件中不存在则返回False
	"""
	isSucceed = False
	try:
		search_tag = {'搜索中': None,
		              '未搜索': None,
		              '已搜索': None}

		DOMTree = xml.dom.minidom.parse(path)
		search_status = DOMTree.documentElement

		for tag in search_tag.keys():
			search_tag[tag] = search_status.getElementsByTagName(tag)[0]

		for elem_status in search_tag.values():
			key_words = elem_status.getElementsByTagName('关键词') \
				if elem_status is not None else []

			for key_word in key_words:
				if key_word.childNodes[0].data.lower() == search_item.lower() \
						if ignore_case else key_word.childNodes[0].data == search_item:
					elem_status.removeChild(key_word)
					if item_status == ItemStatus.IN_SEARCH:
						isSucceed = True
						search_tag['搜索中'].appendChild(key_word)
						break
					elif item_status == ItemStatus.NO_SEARCH:
						isSucceed = True
						search_tag['未搜索'].appendChild(key_word)
						break
					elif item_status == ItemStatus.SEARCH_DONE:
						isSucceed = True
						search_tag['已搜索'].appendChild(key_word)
						break
					else:
						return isSucceed
			if isSucceed:
				break

		if isSucceed:
			xml_str = DOMTree.toprettyxml(indent='\t', newl='\n', encoding='utf-8').decode('utf-8')
			xml_compile = re.compile(r'\n[\n\t\s]+\n')
			xml_str = xml_compile.sub('\n', xml_str)
			with open(path + '.tmp', 'w', encoding='utf-8') as fid:
				fid.write(xml_str)

			os.remove(path)
			os.rename(path + '.tmp', path)
	except Exception as ex:
		if os.path.exists(path + '.tmp'):
			os.remove(path + '.tmp')
		show_warning('获取关键词失败！\n%s：%s' % (set_search_item.__name__, ex))
	finally:
		return isSucceed

def __main():
	path = 'num_searcher.cfg'
	set_search_item(path, '例子', ItemStatus.IN_SEARCH, False)
	# print(get_search_item(path))


if __name__ == '__main__':
	__main()
