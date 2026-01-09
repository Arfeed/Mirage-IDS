import importlib.util
import os, sys
import time, datetime


class ModuleHandler:
    '''User Modules handler'''
    def __init__(self, mod_path, module):
        self.module_path = mod_path
        self.module_object = self.load_module(module)
        self.os_name = os.name

        self.monitor = None
        self.honeypots = None

    def load_module(self, module : str):
        '''Loads module by its name'''
        print('[!] Loading selected module...\n')

        print(f'[#] {module} loading')
        try:
            print('[!] Loading specification...')
            spec = importlib.util.spec_from_file_location(module, os.path.abspath(self.module_path)+f'/{module}')
            print('[*] Specification loaded')

            print('[!] Loading module type...')
            module_obj = importlib.util.module_from_spec(spec)
            print('[*] Module type loaded')

            print('[!] Executing module...')
            spec.loader.exec_module(module_obj)
            print('[*] Module executed\n')

        except:
            print('[@] An error occurred while loading the module, exit')
            sys.exit()
        
        print('[*] Selected module were loaded and executed\n')
        return module_obj

    def check_module(self) -> list[tuple]:
        '''Checks if module has Monitor and Honeypots classes. Monitor class is necessary.'''
        print(f'[!] Checking module {self.module_object.__name__}...')

        objects = dir(self.module_object)
        monitor_status = list(map(lambda x: 'Monitor' in x, objects))
        honeypots_status = list(map(lambda x: 'Honeypots' in x, objects))
        if any(monitor_status):
            print('[*] Monitor class found')
        else:
            print('[*] Monitor class not found')

        if any(monitor_status):
            print('[*] Honeypots class found')
        else:
            print('[*] Honeypots class not found')

        pack = (objects[monitor_status.index(True)] if any(monitor_status) else '',
                objects[honeypots_status.index(True)] if any(honeypots_status) else '')
        
        if not ''.join(pack):
            print(f'[@] No classes found, exit')
            sys.exit()
        elif not pack[0]:
            print(f'[@] Monitor class not found, exit')
            sys.exit()
        print(f'[*] Found classes:', ', '.join(pack), '\n')

        return pack
    

    def start_mon(self, mon : str) -> None:
        '''Creates Monitor class example'''
        try:
            print('[!] Starting Monitor...')
            self.monitor = getattr(self.module_object, mon)()
            print('[*] Monitor started')
        except:
            print('[@] Error occured while monitor starting, exit')
            sys.exit()
    
    def start_hon(self, hon : str, amount : int) -> None:
        '''Creates Honeypots class example'''
        try:
            print('[!] Starting Honeypots...')
            self.honeypots = getattr(self.module_object, hon)()
            self.honeypots.place_honeypots(self.monitor, amount)
            print('[*] Honeypots started')
        except:
            print('[@] Error occured while honeypots starting, exit')
            sys.exit()

class Interface:
    '''Interface for event monitoring.'''
    def __init__(self, module_handler : ModuleHandler):
        self.module_handler = module_handler

        self.header = ['Date', 'Path', 'IsHoneypot']
        self.delay = 0
        self.amount = 0

    def __ans_check(self, f, n : int):
        tmp = n
        while tmp == n:
            tmp = f()
        return tmp

    def __extract_suspects(self, suspects_map : dict[str, list]) -> list:
        '''Extracts suspects from suspects map to list'''
        res = []
        for k in suspects_map.keys():
            res.extend(suspects_map[k])
        return res


    def select_classes(self, classes : list[str]) -> tuple:
        '''Selects module classes that will be used'''
        if classes[1] == '':
            ans = input('[?] There is no Honeypots class. Honeypots technology is not unavailable. Want to continue(y/n)?: ')
            if ans == 'y':
                print('[*] System will work without Honeypots technology\n')
                return (classes[0], '')

            elif ans == 'n':
                print('[*] Exit\n')
                sys.exit()

        else:
            ans = input('[?] There is Honeypots class. Want to use Honeypots technology(y/n)?: ')
            if ans == 'y':
                print('[*] System will work with Honeypots technology\n')

                self.amount = self.__ans_check(self.select_amount, -1)

                return (classes[0], classes[1])

            elif ans == 'n':
                print('[*] System will work without Honeypots technology\n')
                return (classes[0], '')

    def select_delay(self) -> int:
        '''Sets delay for checks'''
        try:
            delay = int(input('[?] Set check delay in seconds: '))
            if delay <= 0:
                print('[@] Delay must be bigger than 0')
                return -1
            
        except ValueError:
            print('[@] Input number please')
            return -1
        
        print(f'[*] Check delay is {delay}\n')
        return delay

    def select_amount(self) -> int:
        '''Sets amount of honeypots'''
        try:
            amount = int(input('[?] Set amount of Honeypots: '))
            if amount < 0:
                print('[@] It must be bigger than 0')
                return -1
            
            print(f'[*] {amount} honeypots will be placed\n')
            return amount
        except ValueError:
            print('[@] Input number please')
            return -1


    def clean_screen(self) -> None:
        if self.module_handler.os_name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def draw_table(self, data : list[list[str]]) -> None:
        if not data: return
        
        w = [max(len(str(r[i])) for r in data) for i in range(len(data[0]))]
        
        sys.stdout.write("┌" + "┬".join("─" * (x + 2) for x in w) + "┐" + '\n')
        
        for row in data:
            line = "│".join(f" {str(x).ljust(w)} " for x, w in zip(row, w))
            sys.stdout.write(f"│{line}│" + '\n')
            if row == data[0]:
                sys.stdout.write("├" + "┼".join("─" * (x + 2) for x in w) + "┤" + '\n')
        
        sys.stdout.write("└" + "┴".join("─" * (x + 2) for x in w) + "┘" + '\n')
        sys.stdout.flush()


    def start_loop(self, selected_classes : tuple[str]) -> None:
        self.module_handler.start_mon(selected_classes[0])
        if selected_classes[1]:
            self.module_handler.start_hon(selected_classes[1], self.amount)

        self.clean_screen()
        self.main_loop()

    def main_loop(self) -> None:
        all_checks = [self.header]
        run = True

        while run:
            check = self.__extract_suspects(self.module_handler.monitor.check())
            for path in check:
                pack = [str(datetime.datetime.now()), path, self.module_handler.honeypots.is_honeypot(path) 
                                                            if self.module_handler.honeypots else False]
                all_checks.append(pack)
            
            self.draw_table(all_checks)
            time.sleep(self.delay)

            self.clean_screen()

    def main(self) -> None:
        self.delay = self.__ans_check(self.select_delay, -1)

        available_classes = self.module_handler.check_module()
        selected_classes = self.select_classes(available_classes)

        self.start_loop(selected_classes)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('[@] Incorrect arguments, exit')
        sys.exit()

    mod_path, module = sys.argv[1:]
    mh = ModuleHandler(mod_path, module)
    inter = Interface(mh)
    inter.main()