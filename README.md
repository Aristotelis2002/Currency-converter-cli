# Currency-converter-cli
## Overview
CLI application that integrates with Fast Forex and lets the user convert currencies with exchange rates from past dates.
## Setup
Clone the repo and create a `config.json` file in the root directory of the application with your Fast Forex API key. Example:
   ```json
   {
       "api_key": "YOUR_API_KEY_HERE"
   }
   ```
### Setup the app for Linux using Nix
Get the package Nix if you don't have it. You don't even need to have Python installed on your machine. Nix will take care of that on a local level. 
Example for Ubuntu:  
```bash
sudo apt install nix
```
After that just run shell.nix script using the command:  
```bash
nix-shell shell.nix
```
After the new shell has loaded run my python program:
```bash
python CurrencyConversion.py 2024-06-04
```
You can pass a different date from the past as long as you follow the YYYY-MM-DD format.

### Setup for Windows
Using pip install the package "requests". Using the same last step as the Linux guide, you can run my program.

## Usage
Follow the prompts to input currency conversion details. You can type 'END' at any time to terminate the application.

## Dependencies
- [Fast Forex API](https://console.fastforex.io/auth/signin): Used to fetch exchange rates for currency conversion.

## License
This project is licensed under the MIT License.
