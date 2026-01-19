import sys, os
import configparser

def show_logo() -> int:
    logo = """
███╗   ███╗ ██╗ ██████╗   █████╗   ██████╗  ███████╗
████╗ ████║ ██║ ██╔══██╗ ██╔══██╗ ██╔════╝  ██╔════╝
██╔████╔██║ ██║ ██████╔╝ ███████║ ██║  ███╗ █████╗  
██║╚██╔╝██║ ██║ ██╔══██╗ ██╔══██║ ██║   ██║ ██╔══╝  
██║ ╚═╝ ██║ ██║ ██║  ██║ ██║  ██║ ╚██████╔╝ ███████╗
╚═╝     ╚═╝ ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝  ╚═════╝  ╚══════╝
"""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

    print(logo, end='')
    print('[*] Mirage v1.0')
    print('[*] https://github.com/Arfeed/Mirage-IDS\n\n')
    return 0

def launch_module(mod_path, module) -> int:
    if os.name == 'nt':
        args = ['start', 'cmd', '/k', 'python', os.path.abspath('./module_handler.py'), f'"{os.path.abspath(mod_path)}"', f'"{module}"']
        os.system(' '.join(args))
        return 0
    else:
        args = ['gnome-terminal', '--', 'python3', os.path.abspath('./module_handler.py'), f'"{os.path.abspath(mod_path)}"', f'"{module}"']
        os.system(' '.join(args))
        return 0

def read_config() -> str:
    print('[!] Reading config...')
    
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        modules_path = config['paths']['modules_path']
    except FileNotFoundError:
        print('[@] Config file not found, exit')
        sys.exit()
    except PermissionError:
        print('[@] Config cannot be read because of permissions, exit')
        sys.exit()
    except KeyError:
        print('[@] Invalid config format, exit')
        sys.exit()

    print(f'[*] Config read successfully, modules path: {modules_path}\n')
    return modules_path

def search_modules(modules_path : str) -> list[str]:
    print(f'[!] Search for modules in "{modules_path}" directory ...')

    modules = os.listdir(modules_path)
    if len(modules) != 0:
        if '__pycache__' in modules:
            modules.pop(modules.index('__pycache__'))
    
    if modules:
        print('[*] Found modules:', ', '.join(modules), '\n')
        return modules
    else:
        print('[@] No modules found, exit')
        sys.exit()

def module_select(modules : list[str]) -> list:
    m_indexes = ', '.join([f'{i} - {modules[i]}' for i in range(len(modules))])
    selected_module = int(input(f'[?] Which modules would you like to use? Write index({m_indexes}): '))

    try:
        selected_module = modules[selected_module]
        print(f'[*] Selected module:', selected_module, '\n')
        return selected_module
    except (ValueError, IndexError):
        print('[@] Invalid index, try again\n')
        return []

def appelation(mod_path, module) -> int:
    ans = ''
    while ans != 'y' and ans != 'n':
        ans = input('[?] Are you sure that you want to run this module(y/n)?: ')

    if ans == 'y':
        print('[!] Launching module...')
        launch_module(mod_path, module)
        print('[*] Module launched successfully')

        ans = ''
        while ans != 'y' and ans != 'n':
            ans = input('[?] Want to launch another module(y/n)?: ')
        
        if ans == 'y':
            return 0
        
        else:
            print('[@] Exit')
            sys.exit()
    else:
        print('[@] Module wont launch, exit')
        sys.exit()

def main():
    run = True
    while run:
        show_logo()
        
        mod_path = read_config()
        modules = search_modules(mod_path)
        
        selected_module = []
        while selected_module == []:
            selected_module = module_select(modules)
        
        appelation(mod_path, selected_module)

if __name__ == '__main__':
    main()