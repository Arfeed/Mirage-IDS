import colorama, time
from local_handler import LocalMonitor,LocalHoneypots
from net_handler import NetMonitor, NetHoneypots

#start file

logo = """
███╗   ███╗ ██╗ ██████╗   █████╗   ██████╗  ███████╗
████╗ ████║ ██║ ██╔══██╗ ██╔══██╗ ██╔════╝  ██╔════╝
██╔████╔██║ ██║ ██████╔╝ ███████║ ██║  ███╗ █████╗  
██║╚██╔╝██║ ██║ ██╔══██╗ ██╔══██║ ██║   ██║ ██╔══╝  
██║ ╚═╝ ██║ ██║ ██║  ██║ ██║  ██║ ╚██████╔╝ ███████╗
╚═╝     ╚═╝ ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝  ╚═════╝  ╚══════╝
"""

#only placeholders for now
if __name__ == '__main__':
    print(logo, end='')
    print('Mirage v1.0')
    print('https://github.com/Arfeed/Mirage-IDS\n\n')
    modules = 'local'#input('choose module(local, net, all): ')
    
    if modules == 'local':
        localm = LocalMonitor()
        localh = LocalHoneypots()

        while True:
            print(localm.check())
            #print(localm.primary_stats)
            time.sleep(0.5)

    else:
        pass
    '''if modules == 'local':
        netm = NetMonitor()
        neth = NetHoneypots()
    
    if modules == 'all':
        localm = LocalMonitor()
        localh = LocalHoneypots()
        netm = NetMonitor()
        neth = NetHoneypots()'''

