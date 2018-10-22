__author__='GG [github.com/hkrware/]'
__version__='1.1.3'
__license__='Apache 2'
__copyright__='Copyright 2018, Dreamflame Inc.'
import subprocess
import sublime
import sublime_plugin
settings='Run As You Type.sublime-settings'
statuserr=True
rayt=None
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
        cmd=subprocess.Popen(cmd,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,**args)
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
        global settings,statuserr,rayt
        self.win=self.view.window()
        rayt=self.win.create_output_panel('rayt_out')
        self.win.run_command('show_panel',{'panel':'output.rayt_out'})
        self.set=sublime.load_settings(settings)
        self.cmd=""
        self.cmds=self.set.get('cmd',{})
        self.syntax=self.view.settings().get("syntax")
        try:
            self.cmd=self.cmds[self.syntax]
        except:
            msg=("No command is set for syntax: "+self.syntax)
            if statuserr:
               sublime.status_message(msg)
            rayt.run_command('rayt_out',{'txt':msg})
            return None
        self.view.run_command('rayt_exec',{'cmd':self.cmd,'shell':True})
