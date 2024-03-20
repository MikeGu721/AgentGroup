import os
import re

def copy_dir(src_path, target_path):
	"""
	将某文件夹整体复制进指定文件夹，两个路径均需已存在
	"""
	if os.path.isdir(src_path) and os.path.isdir(target_path):
		filelist_src = os.listdir(src_path)
		for file in filelist_src:
			path = os.path.join(os.path.abspath(src_path), file)
			if os.path.isdir(path):
				path1 = os.path.join(os.path.abspath(target_path), file)
				if not os.path.exists(path1):
					os.mkdir(path1)
				copy_dir(path, path1)
			else:
				with open(path, 'rb') as read_stream:
					contents = read_stream.read()
					path1 = os.path.join(target_path, file)
					with open(path1, 'wb') as write_stream:
						write_stream.write(contents)
		return True
	else:
		return False


def text_translation(text, trans_table):
    regex = re.compile('|'.join(map(re.escape, trans_table)))
    return regex.sub(lambda match: trans_table[match.group(0)], text)
