import subprocess

class Adb:
    def __init__(self):
        self.start_server()
        if not self.device_available:
            print("No devices detected.")
            exit()

    def start_server(self):
        command = 'adb start-server'
        subprocess.call(command.split(' '))

    def device_available(self):
        commanad = 'adb devices'
        devices = subprocess.Popen(command.split(' '),
                stdout=subprocess.PIPE).communicate()[0].decode('utf-8').split('\n')
        return devices[1]

    @classmethod
    def exec_out(self, args):
        command = ['adb', 'exec-out'] + args.split(' ')
        return subprocess.Popen(command, stdout=subprocess.PIPE).communicate()[0]

    @classmethod
    def shell(self, args):
        command = ['adb', 'shell'] + args.split(' ')
        subprocess.call(command)
