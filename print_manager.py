#   格式：\033[显示方式;前景色;背景色m
#   说明:
#
#   前景色            背景色            颜色
#   ---------------------------------------
#     30                40              黑色
#     31                41              红色
#     32                42              绿色
#     33                43              黃色
#     34                44              蓝色
#     35                45              紫红色
#     36                46              青蓝色
#     37                47              白色
#
#   显示方式           意义
#   -------------------------
#      0           终端默认设置
#      1             高亮显示
#      4            使用下划线
#      5              闪烁
#      7             反白显示
#      8              不可见
#
#   例子：
#   \033[1;31;40m    <!--1-高亮显示 31-前景色红色  40-背景色黑色-->
#   \033[0m          <!--采用终端默认设置，即取消颜色设置-->]]]


__STYLE = {
	'fore':
		{  # 前景色
			'black': 30,  # 黑色
			'red': 31,  # 红色
			'green': 32,  # 绿色
			'yellow': 33,  # 黄色
			'blue': 34,  # 蓝色
			'purple': 35,  # 紫红色
			'cyan': 36,  # 青蓝色
			'white': 37  # 白色
		},
	'back':
		{  # 背景
			'black': 40,  # 黑色
			'red': 41,  # 红色
			'green': 42,  # 绿色
			'yellow': 43,  # 黄色
			'blue': 44,  # 蓝色
			'purple': 45,  # 紫红色
			'cyan': 46,  # 青蓝色
			'white': 47  # 白色
		},
	'mode':
		{  # 显示模式
			'mormal': 0,  # 终端默认设置
			'bold': 1,  # 高亮显示
			'underline': 4,  # 使用下划线
			'blink': 5,  # 闪烁
			'invert': 7,  # 反白显示
			'hide': 8,  # 不可见
		},
	'default': {'end': 0}
}


def __use_style(string, mode='', fore='', back=''):
	mode = '%s' % __STYLE['mode'][mode] if mode in __STYLE['mode'] else ''
	fore = '%s' % __STYLE['fore'][fore] if fore in __STYLE['fore'] else ''
	back = '%s' % __STYLE['back'][back] if back in __STYLE['back'] else ''
	style = ';'.join([s for s in [mode, fore, back] if s])
	style = '\033[%sm' % style if style else ''
	end = '\033[%sm' % __STYLE['default']['end'] if style else ''
	return '%s%s%s' % (style, string, end)


def __get_str_width(str_in):
	max_len = 0
	for strline in str_in.splitlines():
		try:
			str_len = len(strline.encode('gbk'))
		except Exception as ex:
			str_len = len(strline.encode('utf-8'))
		if str_len > max_len:
			max_len = str_len
	return max_len


def show_error(error_massage, have_border=False):
	if have_border:
		massage_width = __get_str_width(error_massage)
		error_massage = '%s\n%s\n%s' % ('*' * massage_width, error_massage, '*' * massage_width)
	print(__use_style(error_massage, 'bold', 'red'))


def show_warning(warning_massage, have_border=False):
	if have_border:
		massage_width = __get_str_width(warning_massage)
		warning_massage = '%s\n%s\n%s' % ('*' * massage_width, warning_massage, '*' * massage_width)
	print(__use_style(warning_massage, 'bold', 'yellow'))


def show_emphasize(emphasize_massage, have_border=False):
	if have_border:
		massage_width = __get_str_width(emphasize_massage)
		emphasize_massage = '%s\n%s\n%s' % ('*' * massage_width, emphasize_massage, '*' * massage_width)
	print(__use_style(emphasize_massage, 'bold', 'cyan'))


def __main():
	show_error('错误！', True)
	show_warning('警告！')
	show_emphasize('强调！')


if __name__ == '__main__':
	__main()
