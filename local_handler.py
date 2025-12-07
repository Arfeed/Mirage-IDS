import os
from json import load
from hashlib import md5

class LocalMonitor:
    '''Monitor for local files(and processes(?) soon)'''
    def __init__(self):
        self.__determine_vals()
        self.__set_primary_stats()
    
    def __determine_vals(self) -> None:
        '''Parses .json file and formats it to make proper paths from it'''
        with open('./data.json', 'r') as data:
            self.__valuables : dict = load(data)['tvaluable'][0]

        for k in self.__valuables.keys():
            for i in range(len(self.__valuables[k])):
                self.__valuables[k][i] = self.__valuables[k][i].replace('%username%', os.getlogin())

    def __set_primary_stats(self) -> None:
        '''Sets primary values of all files'''
        self.primary_stats : dict = {}
        for k in self.__valuables.keys():
            self.primary_stats[k] = []

            for i in range(len(self.__valuables[k])):
                try:
                    if k == 'dirs':
                        self.primary_stats[k].append(os.path.getmtime(self.__valuables[k][i]))
                    elif k == 'files':
                        pack = []
                        with open(self.__valuables[k][i], 'rb') as file:
                            pack.append(md5(file.read()))
                        pack.append(os.path.getatime(self.__valuables[k][i]))
                        self.primary_stats[k].append(pack)
                    elif k == 'logs':
                        self.primary_stats[k].append(len(os.listdir(self.__valuables[k][i])))
                
                except FileExistsError:
                    if k == 'files':
                        self.primary_stats[k].append((0, 0))
                    else:
                        self.primary_stats[k].append(0)
                except PermissionError:
                    if k == 'files':
                        self.primary_stats[k].append((0, 0))
                    else:
                        self.primary_stats[k].append(0)

    def __check_logs(self) -> list:
        '''Checks valuable logs'''
        suspects = []

        for i, file in enumerate(self.__valuables['logs']):
            try:
                if len(os.listdir(self.__valuables['logs'][i])) < self.primary_stats['logs'][i]:
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
            if self.primary_stats['files'][i] == (0, 0):
                continue

            try:
                if os.stat(file).st_atime != self.primary_stats['files'][i][1]:
                    suspects.append(i)
                    print('t', os.stat(file).st_atime, self.primary_stats['files'][i][1])
                    continue

                with open(file, 'rb') as data:
                    if md5(data.read()).digest().hex() != self.primary_stats['files'][i][0].digest().hex():
                        suspects.append(i)
                        print('h', i)

            except FileExistsError:
                continue
            except PermissionError:
                continue
        
        return suspects

    def __check_dirs(self) -> list:
        '''Checks valuable dirs'''
        suspects = []

        for i, file in enumerate(self.__valuables['dirs']):
            try:
                if os.path.getmtime(self.__valuables['dirs'][i]) != self.primary_stats['dirs'][i]:
                    suspects.append(i)
                    
            except FileExistsError:
                continue
            except PermissionError:
                continue

        return suspects

    def get_valuables(self) -> dict:
        '''Returns current monitor valuables''' 
        return self.__valuables
    
    def set_valuables(self, new : dict) -> None:
        '''Sets new valuables''' 
        self.__valuables = new

    def check(self) -> dict:
        '''Checks valuables stats'''
        options = {
            'logs':self.__check_logs,
            'files':self.__check_files,
            'dirs':self.__check_dirs
            }
        
        suspects_map = {}

        for k in self.__valuables.keys():
            suspects_map[k] = options[k]()

        if suspects_map['logs'] == [] and suspects_map['dirs'] == [] and suspects_map['files'] == []:
            self.__set_primary_stats()

        return suspects_map

class LocalHoneypots:
    '''Honeypots manager for local machine'''
    def __init__(self):
        pass