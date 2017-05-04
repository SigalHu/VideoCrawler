from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import asyncio
import os
import re
import time
from print_manager import *
import dir_helper

__task_num = 0

async def __fetch(web_browser, save_path, child_handle, tag_child_page, is_covered=False, time_out=120):
	global __task_num
	subfolder_path = None
	save_item = tag_child_page.find('date').string
	try:
		# 初始化
		js_title_init = '''document.title = "";'''
		web_browser.switch_to.window(child_handle)
		web_browser.maximize_window()
		web_browser.execute_script(js_title_init)

		# 打开页面
		js_load_page = '''
		window.location.href = "%s";''' % tag_child_page.attrs['href']
		web_browser.execute_script(js_load_page)
		print('打开%s页面...' % save_item)

		# 指定存放路径
		subfolder_name = '%s %s' % (save_item, tag_child_page.find('img').attrs['title'])
		subfolder_name = dir_helper.get_valid_name(subfolder_name[:50])
		subfolder_path = os.path.join(save_path, subfolder_name)
		png_num = 0
		if os.path.exists(subfolder_path):
			png_num_str = ''
			for png_file in os.listdir(subfolder_path):
				if os.path.isdir(png_file):
					continue
				if png_file.lower().endswith('.png'):
					png_num += 1
				else:
					png_num_str = png_file
			if str(png_num) == png_num_str:
				print('%s已存在！' % save_item)
				return
			elif not is_covered:
				subfolder_path += '+'
				while os.path.exists(subfolder_path):
					subfolder_path += '+'
				os.mkdir(subfolder_path)
		else:
			os.mkdir(subfolder_path)
		print('等待%s页面加载...' % save_item)

		js_document_complete = '''
		if(document.title && document.readyState=="complete"){
			document.title = "%s加载完成";
		}''' % save_item
		time_spend = 0
		while True:
			# 判断页面是否加载完成
			web_browser.switch_to.window(child_handle)
			web_browser.execute_script(js_document_complete)

			if web_browser.title == '%s加载完成' % save_item:
				soup = BeautifulSoup(web_browser.page_source, 'html.parser')
				# 获取大图标签
				tag_big_img = soup.find('a', attrs={'class': 'bigImage'})
				if tag_big_img is not None:
					break
			else:
				if time_spend < time_out:
					time_wait = __task_num * 0.1
					await asyncio.sleep(time_wait)
					time_spend += time_wait
				else:
					raise Exception('请求超时！')
		print('%s加载完成！' % save_item)

		# 打开大图页面
		web_browser.switch_to.window(child_handle)
		web_browser.execute_script(js_title_init)

		js_load_page = '''
		window.location.href = "%s";''' % tag_big_img.attrs['href']
		web_browser.execute_script(js_load_page)
		print('开始保存%s...' % save_item)

		# 获取所有样图标签，并保存总数
		tag_sample_imgs = soup.find_all('a', attrs={'class': 'sampleImage'})
		with open(os.path.join(subfolder_path, '%d' % (len(tag_sample_imgs) + 1)), 'w') as fid:
			pass
		if png_num == len(tag_sample_imgs) + 1:
			print('%s已存在！' % save_item)
			return

		js_image_complete = '''
		var imgs = document.getElementsByTagName("img");
		if(document.title && imgs && imgs.length > 0)
			if(imgs[0].complete)
				document.title = "%s大图加载完成";''' % save_item
		time_spend = 0
		while True:
			# 判断图片是否加载完成
			web_browser.switch_to.window(child_handle)
			web_browser.execute_script(js_image_complete)

			if web_browser.title == '%s大图加载完成' % save_item:
				# 保存大图
				imgSize = web_browser.find_element_by_xpath('//img').size
				web_browser.set_window_size(imgSize['width'], imgSize['height'])
				web_browser.save_screenshot(os.path.join(subfolder_path, '0.png'))
				web_browser.maximize_window()
				break
			else:
				if time_spend < time_out:
					time_wait = __task_num * 0.1
					await asyncio.sleep(time_wait)
					time_spend += time_wait
				else:
					raise Exception('请求超时！')

		for tag_sample_img, ii in zip(tag_sample_imgs, range(1, len(tag_sample_imgs)+1)):
			# 打开样图页面
			web_browser.switch_to.window(child_handle)
			web_browser.execute_script(js_title_init)

			js_load_page = '''
			window.location.href = "%s";''' % tag_sample_img.attrs['href']
			web_browser.execute_script(js_load_page)

			js_image_complete = '''
			var imgs = document.getElementsByTagName("img");
			if(document.title && imgs && imgs.length > 0)
				if(imgs[0].complete)
					document.title = "%s样图%d加载完成";''' % (save_item, ii)
			time_spend = 0
			while True:
				# 判断图片是否加载完成
				web_browser.switch_to.window(child_handle)
				web_browser.execute_script(js_image_complete)

				if web_browser.title == '%s样图%d加载完成' % (save_item, ii):
					# 保存样图
					imgSize = web_browser.find_element_by_xpath('//img').size
					web_browser.set_window_size(imgSize['width'], imgSize['height'])
					sample_img_path = os.path.join(subfolder_path, '%d.png' % ii)
					web_browser.save_screenshot(sample_img_path)
					web_browser.maximize_window()
					break
				else:
					if time_spend < time_out:
						time_wait = __task_num * 0.1
						await asyncio.sleep(time_wait)
						time_spend += time_wait
					else:
						raise Exception('请求超时！')

			# 若样图不存在则保存预览图
			if os.path.getsize(sample_img_path) < 10 * 1024:
				# 打开预览图页面
				web_browser.switch_to.window(child_handle)
				web_browser.execute_script(js_title_init)

				js_load_page = '''
				window.location.href = "%s";''' % tag_sample_img.div.img.attrs['src']
				web_browser.execute_script(js_load_page)

				js_image_complete = '''
				var imgs = document.getElementsByTagName("img");
				if(document.title && imgs && imgs.length > 0)
					if(imgs[0].complete)
						document.title = "%s预览图%d加载完成";''' % (save_item, ii)
				time_spend = 0
				while True:
					# 判断图片是否加载完成
					web_browser.switch_to.window(child_handle)
					web_browser.execute_script(js_image_complete)

					if web_browser.title == '%s预览图%d加载完成' % (save_item, ii):
						# 保存预览图
						imgSize = web_browser.find_element_by_xpath('//img').size
						web_browser.set_window_size(imgSize['width'], imgSize['height'])
						web_browser.save_screenshot(sample_img_path)
						web_browser.maximize_window()
						break
					else:
						if time_spend < time_out:
							time_wait = __task_num * 0.1
							await asyncio.sleep(time_wait)
							time_spend += time_wait
						else:
							raise Exception('请求超时！')
	except Exception as ex:
		show_error('%s错误：%s' % (save_item, ex))

		if is_covered:
			if os.path.isdir(subfolder_path) and len(os.listdir(subfolder_path)) <= 1:
				dir_helper.remove_all_files(subfolder_path)
		else:
			if os.path.isdir(subfolder_path):
				dir_helper.remove_all_files(subfolder_path)

		return tag_child_page
	finally:
		__task_num -= 1
		web_browser.switch_to.window(child_handle)
		web_browser.close()
		print('关闭%s页面！' % save_item)


def search_and_save(phantomJS_path, search_content, loop, save_path='', is_covered=False, page_start=1, timeout=120):
	global __task_num
	web_browser = None

	try:
		# 配置保存文件夹
		folder_name = dir_helper.get_valid_name(search_content)
		if save_path != '' and not os.path.isdir(save_path):
			show_error('文件夹%s不存在！' % save_path, True)
			return
		save_path = os.path.join(save_path, folder_name)
		if not os.path.exists(save_path):
			os.mkdir(save_path)

		# 获取起始页数
		if page_start == 1:
			page_list = []
			page_compile = re.compile(r'^\d+$')
			for file in os.listdir(save_path):
				if os.path.isdir(file):
					continue
				page_nums = page_compile.findall(file)
				for page_num in page_nums:
					page_list.append(int(page_num))

			if page_list:
				page_list.sort()
				page_start = page_list.pop()
				for page in page_list:
					old_page_file = os.path.join(save_path, str(page))
					try:
						os.remove(old_page_file)
					except Exception as ex:
						pass

		# 打开浏览器
		web_browser = webdriver.PhantomJS(executable_path=phantomJS_path,
		                                  service_args=['--disk-cache=yes'])
		web_browser.set_page_load_timeout(timeout)
		web_browser.maximize_window()
		web_root_handle = web_browser.current_window_handle
		print('打开浏览器！')

		while True:
			# 测试连接
			print('打开测试页面...')
			web_browser.switch_to.window(web_root_handle)
			web_browser.get('https://ww.baidu.com')
			print(web_browser.title)

			# 获取搜索结果
			url = 'https://url/search/%s/page/%d' % (search_content, page_start)
			show_emphasize('获取%s第%d页搜索结果...' % (search_content, page_start), True)
			with open(os.path.join(save_path, str(page_start)), 'w') as fid:
				old_page_file = os.path.join(save_path, str(page_start-1))
				if os.path.exists(old_page_file):
					try:
						os.remove(old_page_file)
					except Exception as ex:
						pass
			# web_browser.get(url)

			# 初始化
			js_title_init = '''document.title = "";'''
			web_browser.switch_to.window(web_root_handle)
			web_browser.execute_script(js_title_init)

			# 打开页面
			js_load_page = '''
			window.location.href = "%s";''' % url
			web_browser.execute_script(js_load_page)

			js_document_complete = '''
			if(document.title && document.readyState=="complete"){
				document.title = "加载完成";
			}'''
			time_spend = 0
			while True:
				time.sleep(0.1)
				time_spend += 0.1
				# 判断页面是否加载完成
				web_browser.execute_script(js_document_complete)
				if web_browser.title == '加载完成':
					break
				elif time_spend > timeout:
					raise Exception('网页加载超时！')

			soup = BeautifulSoup(web_browser.page_source, 'html.parser')
			results = soup.find_all('a', attrs={'class': 'movie-box'})
			if len(results) == 0:
				# print(web_browser.page_source)
				show_emphasize('%s全部搜索完毕！' % search_content, True)
				break
			else:
				repeat_count = 0
				repeat_max = 3
				while len(results) > 0:
					repeat_count += 1
					# 打开子标签页
					js_open_page = '''
					for(var ii=0;ii<%d;ii++)
						window.open();
					''' % len(results)
					web_browser.switch_to.window(web_root_handle)
					web_browser.execute_script(js_open_page)

					# 显示信息
					msg = '准备搜索...'
					for result, ii in zip(results, range(len(results))):
						if ii % 10 == 0:
							msg += '\n'
						msg += ' ' + result.find('date').string
					show_emphasize(msg, True)

					# 获取子标签页句柄
					web_child_handles = web_browser.window_handles
					web_child_handles.remove(web_root_handle)

					# 使用协程
					__task_num = len(results) + 1
					tasks = [asyncio.ensure_future(__fetch(web_browser,
					                                       save_path,
					                                       web_child_handles[ii],
					                                       results[ii],
					                                       is_covered,
					                                       timeout),
					                               loop=loop) for ii in range(len(results))]
					tasksDone, tasksPending = loop.run_until_complete(asyncio.wait(tasks))
					results = []
					for taskDone in tasksDone:
						if taskDone.result():
							results.append(taskDone.result())

					# 关闭所有子标签
					web_child_handles = web_browser.window_handles
					web_child_handles.remove(web_root_handle)
					for child_handle in web_child_handles:
						web_browser.switch_to.window(child_handle)
						web_browser.close()

					# 显示信息
					if len(results) > 0:
						msg = ''
						for result, ii in zip(results, range(1, len(results)+1)):
							msg += result.find('date').string + ' '
							if ii % 10 == 0:
								msg += '\n'
						if msg.endswith('\n'):
							msg += '搜索失败！'
						else:
							msg += '\n搜索失败！'
						show_emphasize(msg, True)

						if repeat_count >= repeat_max:
							raise Exception('搜索次数超过上限！')
					else:
						show_emphasize('第%d页搜索完毕，结果已保存！' % page_start)
				page_start += 1
	except Exception as ex:
		show_error('%s：%s' % (search_and_save.__name__, ex), True)
	else:
		return save_path
	finally:
		if web_browser is not None:
			print('关闭浏览器！')
			web_browser.quit()
