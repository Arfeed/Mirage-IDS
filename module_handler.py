import importlib.util
import inspect
import os

from sys import exit, stdout, argv
from datetime import datetime
from time import sleep


class Interface:
    '''Abstract class for beautiful interface'''
    def __init__(self):
        pass
    
    def print_info(self, message : str) -> None:
        '''Prints info message'''
        print(f'[*] {message}')
    
    def print_action(self, message : str) -> None:
        '''Prints action message'''
        print(f'[!] {message}')

    def get_input(self, message : str) -> str:
        '''Gets user input'''
        return input(f'[?] {message}')

    def exit(self, message : str) -> None:
        '''Closes program with error message'''
        print(f'[@] {message}')
        input('Press any key to continue')
        exit()


class ModuleHandler(Interface):
    '''User Modules handler'''
    def __init__(self, mod_path : str, module : str):
        super().__init__()

        self.module_path : str = mod_path
        self.module_object = self.load_module(module)
        self.os_name : str = os.name

        self.monitor = None
        self.honeypots = None
        

    def load_module(self, module : str):
        '''Loads module by its name'''
        self.print_action('Loading selected module...\n')

        self.print_info(f'{module} loading')
        try:
            self.print_action('Loading specification...')
            spec = importlib.util.spec_from_file_location(module, os.path.abspath(self.module_path)+f'/{module}')
            self.print_info('Specification loaded')

            self.print_action('Loading module type...')
            module_obj = importlib.util.module_from_spec(spec)
            self.print_info('Module type loaded')

            self.print_action('Executing module...')
            spec.loader.exec_module(module_obj)
            self.print_info('Module executed\n')

        except:
            self.exit('An error occurred while loading the module, exit')
        
        self.print_info('Selected module were loaded and executed\n')
        return module_obj

    def select_params(self, target_class) -> list:
        '''Sets module params'''
        self.print_action('Checking available parameters for classes...\n')
        sig = inspect.signature(target_class.__init__)

        new_values = []
        for param in sig.parameters.values():
            #dont touch self
            if param.name == 'self':
                new_values.append('')
                continue

            if param.kind not in (param.VAR_POSITIONAL, param.VAR_KEYWORD):#not positional and not keyword
                #has default value
                if param.default != inspect.Parameter.empty:
                    self.print_info(f'Parameter {param.name} was found, the standard value is {param.default}')
                    new = self.get_input(f'Set parameter {param.name}(if you want to leave default value, press Enter): ')

                    if new == '':
                        new_values.append(param.default)
                    else:
                        new_values.append(new)

                #has not default value
                else:
                    self.print_info(f'Parameter {param.name} was found, it hasnt default value')
                    new = self.get_input(f'Set parameter {param.name}: ')
                    new_values.append(new)

            else:
                self.print_info(f'Parameter {param.name} is invalid, cannot load. Module behavior might be undefined')
        
        self.print_info('Current parameters:')
        for i, param in enumerate(sig.parameters.values()):
            if new_values[i] == '':
                print(f'{param.name} = {param.default}')
            else:
                print(f'{param.name} = {new_values[i]}')

        ans = self.get_input('Set parameters(y/n)?: ')
        if ans == 'y':
            return new_values[1:]#except self
        else:
            return -1


    def check_module(self) -> list[tuple]:
        '''Checks if module has Monitor and Honeypots classes. Monitor class is necessary.'''
        self.print_action(f'Checking module {self.module_object.__name__}...')

        objects = dir(self.module_object)
        monitor_status = list(map(lambda x: 'Monitor' in x, objects))
        honeypots_status = list(map(lambda x: 'Honeypots' in x, objects))

        if any(monitor_status):
            monitor = objects[monitor_status.index(True)]
            self.print_info('Monitor class found')
            self.check_mon(monitor)

        else:
            self.print_info('Monitor class not found')
            self.exit('No Monitor classe in module, exit')

        if any(honeypots_status):
            honeypots = objects[honeypots_status.index(True)]
            self.print_info('Honeypots class found')
            honeypots = self.check_hon(honeypots)

        else:
            self.print_info('Honeypots class not found')
            honeypots = ''

        pack = (monitor, honeypots)

        self.print_info(f'Found classes: {', '.join(pack)}\n')

        return pack

    def check_mon(self, monitor : str) -> int:
        '''Checks if Monitor class is correct'''
        mon_objects = dir(getattr(self.module_object, monitor))

        #check() method check
        if 'check' in mon_objects:
            self.print_info('check() method found')
        else:
            self.exit('No check() method in Monitor class, exit')
        
        return 0

    def check_hon(self, honeypots : str) -> str:
        '''Checks if Honeypots class is correct'''
        hon_objects = dir(getattr(self.module_object, honeypots))

        #place_honeypots() method check
        if 'place_honeypots' in hon_objects:
            self.print_info('place_honeypots() method found')
        else:
            self.print_info('No place_honeypots() method in Honeypots class, honeypots technology is unavailable')
            honeypots = ''
        
        #is_honeypot() method check
        if 'is_honeypot' in hon_objects:
            self.print_info('is_honeypot() method found')
        else:
            self.print_info('No is_honeypot() method in Honeypots class, honeypots technology is unavailable')
            honeypots = ''
        
        return honeypots

    def start_mon(self, mon : str) -> None:
        '''Creates Monitor class example'''
        try:
            self.print_action('Starting Monitor...')

            tmp = self.select_params(getattr(self.module_object, mon))
            while tmp == -1:
                tmp = self.select_params(getattr(self.module_object, mon))
            
            self.monitor = getattr(self.module_object, mon)(*tmp)

            self.print_info('Monitor started\n')
        except Exception as e:
            self.exit(f'{e} - error occured while monitor starting, exit')
    
    def start_hon(self, hon : str, amount : int) -> None:
        '''Creates Honeypots class example'''
        try:
            self.print_action('Starting Honeypots...')

            tmp = self.select_params(getattr(self.module_object, hon))
            while tmp == -1:
                tmp = self.select_params(getattr(self.module_object, hon))
            self.honeypots = getattr(self.module_object, hon)(*tmp)

            self.honeypots.place_honeypots(self.monitor, amount)
            self.print_info('Honeypots started\n')
        except Exception as e:
            self.exit(f'{e} - error occured while honeypots starting, exit')


class IOHandler(Interface):
    '''Interface for event monitoring.'''
    def __init__(self, module_handler : ModuleHandler):
        super().__init__()

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
            ans = self.get_input('There is no Honeypots class. Honeypots technology is unavailable. Want to continue(y/n)?: ')
            if ans == 'y':
                self.print_info('System will work without Honeypots technology\n')
                return (classes[0], '')

            elif ans == 'n':
                self.module_handler.exit('Exit')

        else:
            ans = self.get_input('There is Honeypots class. Want to use Honeypots technology(y/n)?: ')
            if ans == 'y':
                self.print_info('System will work with Honeypots technology\n')
                self.amount = self.__ans_check(self.select_amount, -1)
                return (classes[0], classes[1])

            elif ans == 'n':
                self.print_info('System will work without Honeypots technology\n')
                return (classes[0], '')

    def select_delay(self) -> int:
        '''Sets delay for checks'''
        try:
            delay = int(self.get_input('Set check delay in seconds: '))
            if delay <= 0:
                self.print_info('Delay must be bigger than 0')
                return -1
            
        except ValueError:
            self.print_info('Enter number please')
            return -1
        
        self.print_info(f'Check delay is {delay}\n')
        return delay

    def select_amount(self) -> int:
        '''Sets amount of honeypots'''
        try:
            amount = int(self.get_input('Set amount of Honeypots: '))
            if amount < 0:
                self.print_info('Amount of honeypots must be bigger than 0')
                return -1
            
            self.print_info(f'{amount} honeypots will be placed\n')
            return amount
        except ValueError:
            self.print_info('Enter number please')
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
        
        self.delay = self.__ans_check(self.select_delay, -1)

        self.clean_screen()
        self.main_loop()

    def main_loop(self) -> None:
        all_checks = [self.header]
        run = True

        while run:
            check = self.__extract_suspects(self.module_handler.monitor.check(self.delay))
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

        self.start_loop(selected_classes)



if __name__ == '__main__':
    if len(argv) != 3:
        print('[@] Incorrect arguments, exit')
        exit()

    mod_path, module = argv[1:]
    mh = ModuleHandler(mod_path, module)
    inter = IOHandler(mh)
    inter.main()