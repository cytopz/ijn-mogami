import subprocess

class Adb:
    def __init__(self):
        self.start_server()

    def start_server(self):
        command = ['adb', 'start-server']
        subprocess.call(command)

    def kill_server(self):
        command = ['adb', 'kill-server']
        subprocess.call(command)

    @classmethod
    def exec_out(self, args):
        command = ['adb', 'exec-out'] + args.split(' ')
        res = subprocess.Popen(command, stdout=subprocess.PIPE)
        return res.communicate()[0]

    @classmethod
    def shell(self, args):
        command = ['adb', 'shell'] + args.split(' ')
        subprocess.call(command)
