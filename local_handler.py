import os
from json import load
from hashlib import md5
from random import randint, choice, shuffle

from analyzer import Analyzer


class LocalHandler:
    '''Abstract class for local handlers'''
    def __init__(self):
        self.username = os.getlogin()
        self.windows_replacement_table = {
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
                return 1
            elif (type == 'dirs' or type == 'logs') and os.path.isdir(path):
                return 1
            else:
                return 0
            
        return 0

    def insert_data_win(self, path : str) -> str:
        '''Inserts system data in path with replace table'''
        res = path
        for k, v in self.windows_replacement_table.items():
            res = res.replace(k, v)
        return res


class LocalMonitor(LocalHandler):
    '''Monitor for local files(and processes(?) soon)'''
    def __init__(self, 
                 config_path : str='./data.json'):
        super().__init__()
        self.config_path = config_path

        self.__valuables  = {}
        self.primary_stats  = {}

        self.__determine_vals()
        self.reset_primary_stats()

    def __determine_vals(self) -> None:
        '''Parses .json file and formats it to make proper paths from it'''
        if not self.verify_path(self.config_path, 'files'):
            print('config file does not found, quit')
            return 

        try:
            with open(self.config_path, 'r') as data:
                self.__valuables = load(data)['tvaluable'][0]
        except KeyError:
            print('invalid file format or file does not exists, quit')
            return 1

        for k in self.__valuables.keys():#clear and verify paths
            pack = []

            for i in range(len(self.__valuables[k])):
                clear_path = self.insert_data_win(self.__valuables[k][i])
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
            return 0

    def __check_logs(self) -> list:
        '''Checks valuable logs'''
        suspects = []

        for i, file in enumerate(self.__valuables['logs']):
            try:
                if len(os.listdir(file)) < self.primary_stats['logs'][i][0]:
                    suspects.append(i)
            
            except FileExistsError:
                continue
            except PermissionError:
                continue

        return suspects

    def __check_files(self) -> list:
        '''Checks valuable files'''
        suspects = []
        for i, file in enumerate(self.__valuables['files']):
            if self.primary_stats['files'][i] == (0, 0, 0, 0):
                continue

            try:
                if os.stat(file).st_atime != self.primary_stats['files'][i][1]:
                    suspects.append(i)

                elif self.__calculate_hash(file) != self.primary_stats['files'][i][0]:
                    suspects.append(i)

            except FileExistsError:
                continue
            except PermissionError:
                continue
        
        return suspects

    def __check_dirs(self) -> list:
        '''Checks valuable dirs'''
        suspects = []

        for i, dir in enumerate(self.__valuables['dirs']):
            try:
                if os.path.getmtime(dir) != self.primary_stats['dirs'][i][1]:
                    suspects.append(i)
                    
            except (FileExistsError, PermissionError):
                continue

        return suspects


    def get_valuables(self) -> dict[str : list]:
        '''Returns current monitor valuables''' 
        return self.__valuables
    
    def set_valuables(self, new : dict[str : list]) -> None:
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
                        if k == 'files': self.primary_stats[k].append((0, 0, 0, 0))
                        else: self.primary_stats[k].append(0)

    def check(self) -> dict[str : list]:
            '''Checks valuables stats'''
            options = {
                'logs':self.__check_logs,
                'files':self.__check_files,
                'dirs':self.__check_dirs
                }
            
            suspects_map = {}

            for k in self.__valuables.keys():
                suspects_map[k] = options[k]()

            self.reset_primary_stats()

            return suspects_map


class LocalHoneypots(LocalHandler):
    '''Honeypots manager for local machine'''
    def __init__(self, monitor : LocalMonitor, 
                 names_path : str = './pretty_objects.json',
                 content_path : str = './pretty_contents.json',
                 paths_path : str = './data.json',
                 gen_path : str = './gen_ex.txt'):
        super().__init__()
        self.localm = monitor

        self.pretty_names = {}
        self.pretty_content = []
        self.pretty_paths = []
        

        self.load_paths(names_path,
                        content_path, 
                        paths_path, 
                        gen_path)
        self.__cache_gen_ex()
        self.__set_pretty_objects()
        self.__set_pretty_content()
        self.__set_pretty_paths()
    
    def __set_pretty_objects(self) -> None:
        '''Parses .json file and gets pretty names'''
        if not self.verify_path(self.names_path, 'files'):
            print('file not found, quit')

        try:
            with open(self.names_path, 'r') as file:
                self.pretty_names = load(file)['local']
        except KeyError:
            print('invalid file format, quit')
            return 1

    def __set_pretty_content(self) -> None:
        '''Parses .json file and gets pretty content'''
        if not self.verify_path(self.content_path, 'files'):
            print('file not found, quit')

        try:
            with open(self.content_path, 'r') as file:
                self.pretty_content = load(file)['content']
        except KeyError:
            print('invalid file format, quit')
            return 1
    
    def __set_pretty_paths(self) -> None:
        '''Parses .json data to get paths, verifys and insert data in it'''
        if not self.verify_path(self.paths_path, 'files'):
            print('file not found, quit')

        try:
            with open(self.paths_path, 'r') as file:
                self.pretty_paths = load(file)['bt_places']
        except KeyError:
            print('invalid file format, quit') 
            return 1
        
        pack = []
        for path in self.pretty_paths:#clear and verify path
            clear_path = self.insert_data_win(path)
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

        components.append(str(randint(0, 4096)))
        components.append(hex(randint(0, 4096))[2:])
        components.append(choice(self.gen_cache))
        
        shuffle(components)
        return ''.join(components)
    
    def __insert_passwd(self, content : str) -> str:
        '''Inserts pretty content into string'''
        return content.replace('%password%', self.__make_fpasswd())

    def load_paths(self, names_path : str = '',
                content_path : str = '',
                 paths_path : str = '',
                 gen_path : str = ''):
        '''Loads paths to data files'''

        if names_path: self.names_path = names_path
        if content_path: self.content_path = content_path
        if paths_path: self.paths_path = paths_path
        if gen_path: self.gen_path = gen_path

        self.__set_pretty_objects()
        self.__set_pretty_content()
        self.__set_pretty_paths()

    def place_beartraps(self, amount : int = 3) -> dict:
        '''Places random amount of beartraps with pretty names'''
        new_valuables = self.localm.get_valuables()
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
        
        self.localm.set_valuables(new_valuables)
        self.localm.reset_primary_stats()
        return out
