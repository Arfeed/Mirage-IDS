import importlib.util
import os
from sys import exit, stdout, argv
from datetime import datetime
from time import sleep



class ModuleHandler:
    '''User Modules handler'''
    def __init__(self, mod_path : str, module : str):
        self.module_path : str = mod_path
        self.module_object = self.load_module(module)
        self.os_name : str = os.name

        self.monitor = None
        self.honeypots = None


    def exit(self, message : str):
        '''Closes program with error message'''
        print(f'[@] {message}')
        input('Press any key to continue')
        exit()

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
            self.exit('An error occurred while loading the module, exit')
        
        print('[*] Selected module were loaded and executed\n')
        return module_obj


    def check_mon(self, monitor : str) -> int:
        '''Checks if Monitor class is correct'''
        mon_objects = dir(getattr(self.module_object, monitor))

        #check() method check
        if 'check' in mon_objects:
            print('[*] check() method found')
        else:
            self.exit('No check() method in Monitor class, exit')
        
        return 0

    def check_hon(self, honeypots : str) -> str:
        '''Checks if Honeypots class is correct'''
        hon_objects = dir(getattr(self.module_object, honeypots))

        #place_honeypots() method check
        if 'place_honeypots' in hon_objects:
            print('[*] place_honeypots() method found')
        else:
            print('[@] No place_honeypots() method in Honeypots class, honeypots technology is unavailable')
            honeypots = ''
        
        #is_honeypot() method check
        if 'is_honeypot' in hon_objects:
            print('[*] is_honeypot() method found')
        else:
            print('[@] No is_honeypot() method in Honeypots class, honeypots technology is unavailable')
            honeypots = ''
        
        return honeypots

    def check_module(self) -> list[tuple]:
        '''Checks if module has Monitor and Honeypots classes. Monitor class is necessary.'''
        print(f'[!] Checking module {self.module_object.__name__}...')

        objects = dir(self.module_object)
        monitor_status = list(map(lambda x: 'Monitor' in x, objects))
        honeypots_status = list(map(lambda x: 'Honeypots' in x, objects))

        if any(monitor_status):
            monitor = objects[monitor_status.index(True)]
            print('[*] Monitor class found')
            self.check_mon(monitor)

        else:
            print('[*] Monitor class not found')
            self.exit('No Monitor classe in module, exit')

        if any(honeypots_status):
            honeypots = objects[honeypots_status.index(True)]
            print('[*] Honeypots class found')
            honeypots = self.check_hon(honeypots)

        else:
            print('[*] Honeypots class not found')
            honeypots = ''

        pack = (monitor, honeypots)

        print(f'[*] Found classes:', ', '.join(pack), '\n')

        return pack

    def start_mon(self, mon : str) -> None:
        '''Creates Monitor class example'''
        try:
            print('[!] Starting Monitor...')
            self.monitor = getattr(self.module_object, mon)()
            print('[*] Monitor started')
        except:
            self.exit('Error occured while honeypots starting, exit')
    
    def start_hon(self, hon : str, amount : int) -> None:
        '''Creates Honeypots class example'''
        try:
            print('[!] Starting Honeypots...')
            self.honeypots = getattr(self.module_object, hon)()
            self.honeypots.place_honeypots(self.monitor, amount)
            print('[*] Honeypots started')
        except:
            self.exit('Error occured while honeypots starting, exit')



class Interface:
    '''Interface for event monitoring.'''
    def __init__(self, module_handler : ModuleHandler):
        self.module_handler : ModuleHandler = module_handler

        self.header : list[str] = ['Date', 'Path', 'IsHoneypot']
        self.delay : int = 0
        self.amount : int = 0

    def __ans_check(self, f, n : int):
        '''Cycle for correct answer'''
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


    def select_classes(self, classes : list[str]) -> tuple[str]:
        '''Selects module classes that will be used'''
        if classes[1] == '':
            ans = input('[?] There is no Honeypots class. Honeypots technology is unavailable. Want to continue(y/n)?: ')
            if ans == 'y':
                print('[*] System will work without Honeypots technology\n')
                return (classes[0], '')

            elif ans == 'n':
                self.module_handler.exit('Exit')

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
            print('[@] Enter number please')
            return -1
        
        print(f'[*] Check delay is {delay}\n')
        return delay

    def select_amount(self) -> int:
        '''Sets amount of honeypots'''
        try:
            amount = int(input('[?] Set amount of Honeypots: '))
            if amount < 0:
                print('[@] Amount of honeypots must be bigger than 0')
                return -1
            
            print(f'[*] {amount} honeypots will be placed\n')
            return amount
        except ValueError:
            print('[@] Enter number please')
            return -1


    def clean_screen(self) -> None:
        if self.module_handler.os_name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    def draw_table(self, data : list[list[str]]) -> None:
        if not data: return
        
        w = [max(len(str(r[i])) for r in data) for i in range(len(data[0]))]
        
        stdout.write("┌" + "┬".join("─" * (x + 2) for x in w) + "┐" + '\n')
        
        for row in data:
            line = "│".join(f" {str(x).ljust(w)} " for x, w in zip(row, w))
            stdout.write(f"│{line}│" + '\n')
            if row == data[0]:
                stdout.write("├" + "┼".join("─" * (x + 2) for x in w) + "┤" + '\n')
        
        stdout.write("└" + "┴".join("─" * (x + 2) for x in w) + "┘" + '\n')
        stdout.flush()


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
                pack = [str(datetime.now()), path, self.module_handler.honeypots.is_honeypot(path) 
                                                            if self.module_handler.honeypots else False]
                all_checks.append(pack)
            
            self.draw_table(all_checks)
            sleep(self.delay)

            self.clean_screen()

    def main(self) -> None:
        available_classes = self.module_handler.check_module()
        selected_classes = self.select_classes(available_classes)
        
        self.delay = self.__ans_check(self.select_delay, -1)

        self.start_loop(selected_classes)



if __name__ == '__main__':
    if len(argv) != 3:
        print('[@] Incorrect arguments, exit')
        exit()

    mod_path, module = argv[1:]
    mh = ModuleHandler(mod_path, module)
    inter = Interface(mh)
    inter.main()