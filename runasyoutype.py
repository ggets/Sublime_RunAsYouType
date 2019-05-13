__author__='GG [github.com/hkrware/]'
__version__='1.1.6'
__license__='Apache 2'
__copyright__='Copyright 2019, Dreamflame Inc.'
import subprocess
import sublime
import sublime_plugin
import os
import sys
settings_file='Run As You Type.sublime-settings'
statuserr=True
rayt=None
cmd={}
def plugin_loaded():
    global settings,cmd
    settings=sublime.load_settings(settings_file)
    if settings.has('cmd_custom'):
        if settings.has('cmd'):
            cmd=settings.get('cmd')
        cmd_custom=settings.get('cmd_custom')
        for c in cmd_custom:
            cmd[c]=cmd_custom[c]

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
        (stdout,stderr)=cmd.communicate(self.txt.encode('UTF-8'))
        return (stdout,stderr,cmd.returncode)
    def prep_cmd(self,cmd):
        global statuserr
        try:
            stdout,stderr,status=self.exec_cmd(cmd)
            if not self.expected_returns or status in self.expected_returns:
                sublime.status_message("Successfully executed!")
                return stdout.decode('UTF-8')
        except OSError as e:
            stdout,stderr,status=(None,str(e),e.errno)
        stderr=stderr.decode('utf-8').translate(str.maketrans('','',chr(0x0d)))
        if statuserr:
            sublime.status_message('Error %i executing command [%s]: %s'%(status,self.get_command_as_str(),stderr.replace("\n"," ")))
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
    def run(self,text):
        global cmd,statuserr,rayt
        self.win=self.view.window()
        rayt=self.win.create_output_panel('rayt_out')
        self.win.run_command('show_panel',{'panel':'output.rayt_out'})
        self.cmd=""
        self.syntax=self.view.settings().get("syntax")
        try:
            self.cmd=cmd[self.syntax]
        except:
            msg=("No command is set for syntax: "+self.syntax)
            if statuserr:
               sublime.status_message(msg)
            rayt.run_command('rayt_out',{'txt':msg})
            return None
        # self.cmd=self.cmd.replace("{filename}","")
        self.view.run_command('rayt_exec',{'cmd':self.cmd,'shell':True})
