## Synopsis

Python script to convert Cisco IOS/IOS-XE/NX-OS switch config into YAML data, suitable for use in Ansible.

## Motivation

A simple way to create YAML data from an existing network. This allows migration from old-fashioned manual switch config to an automated "Infrastructure As Code".

## Installation

1. Clone repo
2. Run `pip install -r requirements.txt` to install dependencies.

## Usage

Place Cisco switch config files into `/configurations`. Run the script and YAML files will be generated in `/yaml/configurations`.

### Optional arguments

* Specify an alternative directory for a set of Cisco configs with `--root="foo"`. Output will be generated in `/yaml/foo`.
* Output YAML directly to terminal with `--debug`.
* Override default domain appended to YAML files with `--domain="foo"`.

## Tests

Run `python tests.py`.

## License

MIT license.
