import os
from json import load
from hashlib import md5
from random import randint, choice, shuffle



class LocalHandler:
    '''Abstract class for local handlers'''
    def __init__(self):
        self.username : str = os.getlogin()
        self.windows_replacement_table : dict = {
            '%username%': self.username,
            '%userprofile%' : f'C:\\Users\\{self.username}',
            '%appdata%' : f'C:\\Users\\{self.username}\\AppData\\Roaming',
            '%local%' : f'C:\\Users\\{self.username}\\AppData\\Local',
            '%public%' : 'C:\\Users\\Public',
            '%temp%' : f'C\\Users\\{self.username}\\AppData\\Temp'
        }

    def verify_path(self, path : str, type : str) -> bool:
        '''Verifys path with its type'''
        if os.path.exists(path):
            if type == 'files' and os.path.isfile(path):
                return True
            elif (type == 'dirs' or type == 'logs') and os.path.isdir(path):
                return True
        
        return False

    def format_path(self, path : str) -> str:
        '''Inserts system data in path with replace table'''
        if os.name == 'nt':
            res = path
            for k, v in self.windows_replacement_table.items():
                res = res.replace(k, v)

            return res
        else:
            return path     


class LocalMonitor(LocalHandler):
    '''Monitor for local files(and processes(?) soon). Argument config_path sets path to config .json file with dirs, files and logs to monitor.'''
    def __init__(self, 
                 config_path : str='./data/data.json'):
        super().__init__()
        self.config_path : str = config_path
        self.UNAVAILABLE_FILE : tuple = (0,0,0,0)

        self.__valuables : dict[str : list] = {}
        self.primary_stats : dict[str : list] = {}

        self.__determine_vals()
        self.reset_primary_stats()

    def __determine_vals(self) -> None:
        '''Parses .json file and formats it to make proper paths from it'''
        if not self.verify_path(self.config_path, 'files'):
            print('config file does not found, quit')
            return 

        try:
            with open(self.config_path, 'r') as data:
                self.__valuables = load(data)['valuable'][0]
        except KeyError:
            print('invalid file format or file does not exists, quit')
            return 

        for k in self.__valuables.keys():#clear and verify paths
            pack = []

            for i in range(len(self.__valuables[k])):
                clear_path = self.format_path(self.__valuables[k][i])
                if self.verify_path(clear_path, k):
                    pack.append(clear_path)

            self.__valuables[k] = pack

    def __calculate_hash(self, path: str, buffer_size: int = 65536) -> str:
        '''Calculates buffer hash'''
        md5_hash = md5()
        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(buffer_size), b''):
                    md5_hash.update(chunk)

            return md5_hash.hexdigest()
        
        except (IOError, OSError) as e:
            return ''

    def __check_logs(self) -> list:
        '''Checks valuable logs'''
        suspects = []

        for i, log in enumerate(self.__valuables['logs']):
            try:
                if len(os.listdir(log)) < self.primary_stats['logs'][i][0]:
                    suspects.append(self.__valuables['logs'][i])
            
            except FileExistsError:
                continue
            except PermissionError:
                continue

        return suspects

    def __check_files(self) -> list:
        '''Checks valuable files'''
        suspects = []
        for i, file in enumerate(self.__valuables['files']):
            if self.primary_stats['files'][i] == self.UNAVAILABLE_FILE:
                continue

            try:
                if os.path.getatime(file) != self.primary_stats['files'][i][1]:
                    suspects.append(self.__valuables['files'][i])

                elif os.path.getmtime(file) != self.primary_stats['files'][i][2] or \
                    os.path.getsize(file) != self.primary_stats['files'][i][3]:

                    if self.__calculate_hash(file) != self.primary_stats['files'][i][0]:
                        suspects.append(self.__valuables['files'][i])
                        continue

                    suspects.append(self.__valuables['files'][i])

            except FileExistsError:
                continue
            except PermissionError:
                continue
        
        return suspects

    def __check_dirs(self, delay) -> list:
        '''Checks valuable dirs'''
        suspects = []

        for i, dir in enumerate(self.__valuables['dirs']):
            try:
                if int(os.path.getatime(dir)-self.primary_stats['dirs'][i][0])!=delay:
                    suspects.append(self.__valuables['dirs'][i])

                elif os.path.getmtime(dir) != self.primary_stats['dirs'][i][1]:
                    suspects.append(self.__valuables['dirs'][i])
                    
            except FileExistsError:
                continue
            except PermissionError:
                continue

        return suspects


    def get_valuables(self) -> dict[str, list]:
        '''Returns current monitor valuables''' 
        return self.__valuables
    
    def set_valuables(self, new : dict[str, list]) -> None:
        '''Sets new valuables''' 
        self.__valuables = new
        self.reset_primary_stats()

    def get_config(self) -> str:
        '''Returns path to current config file'''
        return self.config_path

    def set_config(self, new_path : str = '') -> bool:
        '''Sets new path to config file'''
        if new_path:
            if self.verify_path(new_path):
                self.config_path = new_path
                return True
        return False


    def reset_primary_stats(self) -> None:
            '''Sets primary values of all valuables'''
            for k in self.__valuables.keys():
                self.primary_stats[k] = []

                for obj in self.__valuables[k]:
                    try:
                        if k == 'dirs':
                            pack = [os.path.getatime(obj),#ask time
                                    os.path.getmtime(obj),#mod time
                                    os.listdir(obj)]      #objects in dir
                            self.primary_stats[k].append(pack)

                        elif k == 'files':
                            pack = [self.__calculate_hash(obj),#hash
                                    os.path.getatime(obj),     #ask time
                                    os.path.getmtime(obj),     #mod time
                                    os.path.getsize(obj)]      #size
                            self.primary_stats[k].append(pack)

                        elif k == 'logs':
                            pack = [
                                len(os.listdir(obj))#files count
                                ]
                            self.primary_stats[k].append(pack)
                    
                    except (FileExistsError, PermissionError, OSError, FileNotFoundError):
                        if k == 'files': self.primary_stats[k].append(self.UNAVAILABLE_FILE)
                        else: self.primary_stats[k].append(0)

    def check(self, delay : int = 1) -> dict[str : list]:
            '''Checks valuables stats'''
            options = {
                'logs':self.__check_logs,
                'files':self.__check_files,
                'dirs':self.__check_dirs
                }
            
            suspects_map = {}

            for k in self.__valuables.keys():
                if k == 'dirs':
                    suspects_map[k] = options[k](delay)
                    continue
                suspects_map[k] = options[k]()

            self.reset_primary_stats()

            return suspects_map



class LocalHoneypots(LocalHandler):
    '''Honeypots manager for local machine'''
    def __init__(self, names_path : str = './data/pretty_objects.json',
                 content_path : str = './data/pretty_contents.json',
                 gen_path : str = './data/gen_ex.txt',
                 paths_path : str = './data/data.json'):
        super().__init__()
        self.RANDOM_BORDER = 4096

        self.pretty_names : list = []
        self.pretty_content : list = []
        self.pretty_paths : list = []
        self.current_honeypots : list = []

        self.set_paths(names_path,
                        content_path, 
                        paths_path, 
                        gen_path)
    
    def __set_pretty_objects(self) -> None:
        '''Parses .json file and gets pretty names'''
        if not self.verify_path(self.names_path, 'files'):
            print('file not found, quit')

        try:
            with open(self.names_path, 'r') as file:
                self.pretty_names = load(file)['local']
        except KeyError:
            print('invalid file format, quit')
            return 

    def __set_pretty_content(self) -> None:
        '''Parses .json file and gets pretty content'''
        if not self.verify_path(self.content_path, 'files'):
            print('file not found, quit')

        try:
            with open(self.content_path, 'r') as file:
                self.pretty_content = load(file)['content']
        except KeyError:
            print('invalid file format, quit')
            return 
    
    def __set_pretty_paths(self) -> None:
        '''Parses .json data to get paths, verifys and insert data in it'''
        if not self.verify_path(self.paths_path, 'files'):
            print('file not found, quit')

        try:
            with open(self.paths_path, 'r') as file:
                self.pretty_paths = load(file)['bt_places']
        except KeyError:
            print('invalid file format, quit') 
            return 
        
        pack = []
        for path in self.pretty_paths:#clear and verify path
            clear_path = self.format_path(path)
            if self.verify_path(clear_path, 'dirs'):
                pack.append(clear_path)

        self.pretty_paths = pack.copy()

    def __cache_gen_ex(self) -> None:
        '''Caches gen file'''
        with open(self.gen_path, 'r') as file:
            self.gen_cache = file.read().split('\n')

    def __make_fpasswd(self) -> str:
        '''Generates fake password for beartrap'''
        components = []

        components.append(str(randint(0, self.RANDOM_BORDER)))
        components.append(hex(randint(0, self.RANDOM_BORDER))[2:])
        components.append(choice(self.gen_cache))
        
        shuffle(components)
        return ''.join(components)
    
    def __insert_passwd(self, content : str) -> str:
        '''Inserts pretty content into string'''
        return content.replace('%password%', self.__make_fpasswd())


    def set_paths(self, names_path : str = '',
                content_path : str = '',
                 paths_path : str = '',
                 gen_path : str = ''):
        '''Loads paths to data files. If path argument is not defined, it wont change.'''

        if names_path:self.names_path = names_path
        if content_path: self.content_path = content_path
        if paths_path : self.paths_path = paths_path
        if gen_path: self.gen_path = gen_path

        self.__set_pretty_objects()
        self.__set_pretty_content()
        self.__set_pretty_paths()
        self.__cache_gen_ex()

    def get_paths(self) -> tuple:
        ''' Returns current config paths'''
        return (self.names_path,
                self.content_path,
                self.paths_path,
                self.gen_path)

    def is_honeypot(self, path : str) -> bool:
        '''Checks, if object placed in path is a honeypot'''
        if path in self.current_honeypots:
            return True
        return False


    def place_honeypots(self, monitor : LocalMonitor, amount : int = 3) -> list:
        '''Places beartraps with pretty names and reutrns their paths'''
        new_valuables = monitor.get_valuables()
        out = []

        for i in range(amount):
            name = choice(self.pretty_names)
            content = choice(self.pretty_content)
            path = choice(self.pretty_paths)

            full_path = f'{path}\\{name}'

            with open(full_path, 'w') as file:
                file.write(self.__insert_passwd(content))
            
            out.append(full_path)
            new_valuables['files'].append(full_path)
        
        monitor.set_valuables(new_valuables)
        monitor.reset_primary_stats()
        self.current_honeypots = out

        return out
