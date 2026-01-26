# Mirage-IDS
A cross-platform, open-source IDS with Honeypots technology. It features high modularity, easy installation, and flexible configuration.

## General Information

### Installation
1. Clone repository in current working directory  
`git clone https://github.com/Arfeed/Mirage-IDS`  

2. Set config values in `config.ini` file and configs for default modules in `./data` directory
3. Launch start script  
`python3 start.py`

### Features

The key features of Mirage-IDS are:
- Highly modular
- Flexible configuration
- Easy deployment
- Easy to write custom modules
- Use of Honeypots technology

## Technical Information

## Used tech stack
- Python 3+
- JSON

## Architecture
The system has **2** main cores that ensure its operation:
- Start script

- Module Handler

**Start Script** finds modules in the directory specified in the config and sends the selected module to the Module Handler

**Module Handler** handles the work of the module, ensuring its operation and allowing it to interact with the interface.

## Honeypot technology
Honeypot technology involves creating interactive traps designed to attract the attention of an intruder and increase the likelihood of detection before any real damage is done. The traps must be attractive to the attacker, provoking them to interact, which will lead to their discovery.

## Modules construction
Each module must have 1 required and 1 optional class:
 - **Monitor class(required)** - class that monitors the interactions of objects under observation. Must have 'Monitor' substring in its name. Required methods - **check()**
 
 - **Honeypots class(optional)** - class that processes and creates honeypots. Must have 'Honeypots' substring in its name. Required methods - **is_honeypot()**, **place_honeypots()**. place_honeypots() method must accept any argument that associated with Monitor class.

## Requirements
System uses standart Python libs, so there is no requirements.
