# autocode
Simple code generator.


## Setting  Up Templates

- Setup source data for your template.
- Setup the template itself in the templates folder.

## Setting Up Playbooks

- Use the "playbooks" folder to feed your autocode tasks.
- Setup your YAML playbook in the folder.
- No need to use extension names (".yml") when setting up playbooks.

## Running your playbooks

- Use the "runner" folder to setup the list of playbooks you watn to execute.
- Add the name of the playbooks you want to execute.

## References - Data Type Mappers

- Checkout the data_mapper.py file in autocore to see how data types are mapped.



## Usage Guide

Data Types Supported by the Generator:

- int 
- tinyint
- bigint
- boolean
- char
- varchar
- text
- float
- date
- time
- uuid

> Supported implies, the datatypes automatically map to native data types in 
> PostgreSQL, SQLServer, C#, Python (pydantic).