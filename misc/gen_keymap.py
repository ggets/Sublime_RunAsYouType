import os.path
import json
import copy
keymap = {
	"rayt_wparam_cmd": {
		"mac": "shift+f10",
		"pc": "shift+f10"
	},
	"rayt_cmd": {
		"mac": "f10",
		"pc": "f10"
	}
}
header = "// Automatically generated with misc/generate-keymap.py\n"
_dir = os.path.dirname(os.path.abspath(__file__))
def create_record(k, v, os_type):
	if isinstance(v, str):
		v = {"keys": [v]}
	else:
		v = copy.deepcopy(v)
	if os_type in v:
		v['keys'] = [v[os_type]]
	if 'pc' in v:
		del v['pc'] 
	if 'mac' in v:
		del v['mac']
		v['command'] = k
	return v

def generate_keymap_file(path):
	os_type = 'mac' if '(OSX)' in path else 'pc'
	path = os.path.abspath(os.path.join(_dir, path))
	print('Generate %s (%s)' % (path, os_type))
	editor_keymap = [create_record(k, v, os_type) for k, v in keymap.items()]
	content = json.dumps(editor_keymap, indent=2)
	f = open(path, 'w')
	f.write(header + content)
	f.close()
for path in ['../Default (OSX).sublime-keymap', '../Default (Windows).sublime-keymap', '../Default (Linux).sublime-keymap']:
	generate_keymap_file(path)
