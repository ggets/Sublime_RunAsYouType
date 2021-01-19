__author__='GG [github.com/ggetsov/]'
__version__='1.3.4'
__license__='Apache 2'
__copyright__='Copyright 2019, Dreamflame Inc.'
import sublime
import sublime_plugin
import subprocess
import os.path
name																						=os.path.basename(os.path.abspath(os.path.dirname(__file__)))
name																						=name.replace('.sublime-package','')
settings_file																		='%s.sublime-settings'%name
params_file																			='%s_params.json'%name
grammar_file																		='Packages/%s/%s.tmLanguage'%(name,name)
statuserr																				=True
rayt																						=None
syntax																					=''
cmds																						={}
params_header																		="// Command parametters are saved here.\n"
inpanel																					=None
win																							=None
var																							=sublime.active_window().extract_variables()

def plugin_loaded():
	load_cmds()

def load_settings():
	global settings,params,settings_file,params_file
	settings=sublime.load_settings(settings_file)
	params=sublime.load_settings(params_file)

"""Get a setting from current view or global settings object.
	@param	{string}					k										The setting to read.
	@param	{mixed}						d										The default value to return if setting is
																								non-existent in the view or global settings object.
	@return	{mixed}																The setting value or the default one.
"""
def get_setting(k,d=None):
	global settings
	try:
		settings
	except NameError:
		load_settings()
	return settings.get(k,d)

def load_cmds():
	global cmds
	cmds=get_setting('cmd')
	cmd_custom=get_setting('cmd_custom')
	if(settings.has('cmd') and settings.has('cmd_custom')):
		for c in cmd_custom:
			cmds[c]=cmd_custom[c]


class RAYTEvListener(sublime_plugin.EventListener):
	monitored_extensions={'py':True,'sublime-settings':True,'json':True}
	monitored_user_text='User.'
	shift_by_user_dot_length=5 # len(monitored_user_text)
	def GetPluginNameFromPath(self,_path=''):
		global name,var
		_file=_path.split('\\')[-1]
		_ext=_file.split('.')[-1]
		_index=_path.find(name)
		_is_plugin_file=(_index>0)
		_pack=var.get('packages',sublime.packages_path())
		if(_path.find(_pack)>-1):
			_plugin=_path[len(_pack)+1:len(_path)]
		else:
			_plugin=_path
		if(self.monitored_extensions.get(_ext,None)):
			if(_ext=='py'):
				_plugin=_path[_index:(-1*(len(_ext)+1))]
				_plugin_user=_path[_index-self.shift_by_user_dot_length:(-1*(len(_ext)+1))]
				if(_plugin_user.startswith(self.monitored_user_text)):
					_plugin=self.monitored_user_text+_plugin
				return(_plugin,_is_plugin_file)
			else:
				return(_plugin,_is_plugin_file)
		return(None,_is_plugin_file)
	def on_post_save_async(self,_view):
		_file=_view.file_name()
		(_plugin,_is_plugin_file)=self.GetPluginNameFromPath(_file)
		if(_is_plugin_file and (_plugin!=None)):
			if(_plugin.endswith('py')):
				sublime_plugin.reload_plugin(_plugin)
			elif(_plugin.endswith('sublime-settings') or _plugin.endswith('json')):
				load_cmds()

class raytFN(sublime_plugin.TextCommand):
	def apply_settings(self,s):
		for k,v in s.items():
			setattr(self,k,v)
	def run(self,edit,**s):
		global statuserr
		self.apply_settings(s)
		self.txt=self.view.substr(sublime.Region(0,self.view.size()))
		try:
			self.txt=self.prep_cmd(self.cmd)
		except Exception as ex:
			if statuserr:
				sublime.status_message(str(ex))
			return None
			raise
		if self.txt is None:
			self.txt=''
		self.txt=self.txt.translate(str.maketrans('','',chr(0x0d)))
		self.view.run_command('rayt_out',{'txt':self.txt})
class raytOutCommand(raytFN):
	txt=''
	def run(self,edit,**s):
		global rayt
		self.apply_settings(s)
		rayt.run_command("append",{"characters":self.txt})
class raytExecCommand(raytFN):
	cmd=[]
	shell=False
	expected_returns=[0]
	subprocess_args={}
	def exec_cmd(self,cmd):
		args=self.subprocess_args or {}
		args['shell']=self.shell
		if self.view.file_name():
			dirpath=os.path.dirname(self.view.file_name())
		else:
			dirpath=os.getcwd()
		cmd=subprocess.Popen(cmd,
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			cwd=dirpath,**args)
		(stdout,stderr)=cmd.communicate(self.txt.encode('utf-8'))
		return(stdout,stderr,cmd.returncode)
	def prep_cmd(self,cmd):
		global statuserr
		try:
			stdout,stderr,status=self.exec_cmd(cmd)
			if not self.expected_returns or status in self.expected_returns:
				sublime.status_message("Successfully executed!")
				if isinstance(stdout,str):
					stdout=str(stdout)
				else:
					stdout=stdout.decode('utf-8')
				return stdout
		except OSError as e:
			stdout,stderr,status=(None,str(e),e.errno)
		if isinstance(stderr,str):
			stderr=str(stderr)
		else:
			stderr=stderr.decode('utf-8')
		stderr=stderr.translate(str.maketrans('','',chr(0x0d)))
		if statuserr:
			sublime.status_message('Error %i executing command [%s]:%s'%(status,self.get_command_as_str(),stderr.replace("\n"," ")))
		rayt.run_command('rayt_out',{'txt':('Error %i executing command [%s]:\n%s\n'%(status,self.get_command_as_str(False),stderr))})
		return None
	def get_command_as_str(self,short=True):
		c=self.cmd
		if isinstance(c,str):
			return c
		if short:
			return c[0]
		return ' '.join(c)
class raytCmdCommand(sublime_plugin.TextCommand):
	def exec(self):
		global statuserr,rayt,params,inpanel,win
		load_cmds()
		view=self.view
		param=None
		if(isinstance(inpanel,sublime.View) and (inpanel.name()=='rayt_param_input')):
			param=inpanel.substr(sublime.Region(0,inpanel.size()))
			view=inpanel.from_view
			inpanel.close()
			inpanel=None
			win=None
		if(view.window() is not None):
			win=view.window()
		rayt=win.create_output_panel('rayt_out')
		if(win is not None):
			win.run_command('show_panel',{'panel':'output.rayt_out'})
		self.syntax=view.settings().get("syntax")
		if((param is not None) and (isinstance(param,str)) and (params.get(self.syntax) is not param)):
			params.set(self.syntax,param)
			sublime.save_settings(params_file)
		self.cmd=""
		if(win is not None):
			try:
				self.cmd=cmds[self.syntax]
				self.cmd=sublime.expand_variables(self.cmd,win.extract_variables())
			except:
				msg=("No command is set for syntax:"+self.syntax)
				if statuserr:
					sublime.status_message(msg)
				rayt.run_command('rayt_out',{'txt':msg})
				return None
			param=param or params.get(self.syntax)
			if param is not None and len(param):
				self.cmd+=' '+param
				# self.cmd=self.cmd.replace("{filename}","")
			view.run_command('rayt_exec',{'cmd':self.cmd,'shell':True})
	def run(self,edit):
		self.exec()
class raytWparamCmdCommand(raytCmdCommand):
	input_message																	="Parameters:"
	default_input																	=""
	process_panel_input														=lambda s,i:''
	def on_panel_change(self,val):
		if not val and self.erase:
			self.undo()
			self.erase=False
			return
		def inner_insert():
			self.view.run_command(self.name(),dict(panel_input=val))
		self.undo()
		sublime.set_timeout(inner_insert,0)
	def undo(self):
		if self.erase:
			sublime.set_timeout(lambda:self.view.run_command('undo'),0)
	def on_panel_done(self,val):
		self.view.run_command('rayt_cmd')
	def run(self,edit,panel_input=None,**kwargs):
		global inpanel
		if panel_input is None:
			self.syntax=self.view.settings().get("syntax")
			param=params.get(self.syntax)
			self.default_input=''
			if param is not None:
				self.default_input=param
			self.edit=edit
			self.setup(edit,self.view,**kwargs)
			self.erase=False
			inpanel=self.view.window().show_input_panel(
				self.input_message,
				self.default_input,
				self.on_panel_done,
				self.on_panel_change,
				self.undo)
			inpanel.from_view=self.view
			inpanel.set_name('rayt_param_input');
			inpanel.sel().clear()
			inpanel.sel().add(sublime.Region(0,inpanel.size()))
			self.run_on_input(edit,self.view,panel_input)
			if grammar_file:
				inpanel.set_syntax_file(grammar_file)
				panel_setting=inpanel.settings().set
				panel_setting('line_numbers',							False)
				panel_setting('gutter',										False)
				panel_setting('auto_complete',						False)
				panel_setting('tab_completion',						False)
		else:
			self.run_on_input(edit,self.view,panel_input)
	def setup(self,edit,view,**kwargs):
		pass
	def run_on_input(self,edit,view,panel_input):
		view=self.view
		cmd_input=self.process_panel_input(panel_input) or ''
		try:
			self.erase=self.run_command(edit,view,cmd_input) is not False
		except:
			pass
