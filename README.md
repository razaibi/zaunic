# Zaunic
Configurable, easy-to-use accelerator.

![alt text](https://github.com/razaibi/zaunic/raw/main/project_assets/zaunic_logo_color.png)

## Quick Start Guide

### Check Dependencies

- Ensure you have Python 3 installed.
- Install dependencies using the below command:

```
pip install -r requirements.txt
```

### Setup Up Template(s)

- In the templates folder, navigate to an existing directory or create a new one.
- Templates can be of two types:

> **Short Template** for single line or short templates that can be grouped together in one file. These are setup in a *.yml* file (for now). Below is an example of a couple of short templates from the sample *templates/azurecli/folder/sample-resource.yml*. 

```
---
 create_group: "az group create --name {{ resource_group_name }} --location {{ location }}"
 update: "az update"

```


> **Long Template** for complex and long templates that require complete individual files. Below is an example of a long template from the sample *templates/postgresql/sample_ddl.j2*.

```
{%-for database in databases %}
{%-for table in database['tables'] %}
CREATE TABLE {{table.name}} (
    {%for column in table['columns']-%}
    {%-if 'foreign_key' in column and column['foreign_key'] is not none %}FOREIGN KEY ({{column.name}}) 
        REFERENCES {{column['foreign_key']['reference_entity']}} ({{column['foreign_key']['reference_column']}})
    {%-else-%}
    {{column.name}} {{column.type}} {%-if column['is_primary'] == True %} PRIMARY KEY {%-endif %}
    {%-if column['is_required'] == True %} NOT NULL {% else %} NULL {%-endif%}
    {%-endif-%}
    {%-if not loop.last-%},{%-endif %}
    {%endfor%}
);
{% endfor-%}
{% endfor-%}
```

**Note how the formats for long and short templates are different (.yml vs .j2)**


### Setup Source Data

For code or configs to be generated, specify the source data that needs to be used. Navigate to the "data" folder and setup your yaml file. Source data can be flat or nested. Below is an example from *sample-resource.yml* file from the *data* folder.



### Set Up Taskflows

- Use the "taskflows" folder to manage your zaunic tasks.
- Setup your YAML taskflow in the folder. Below is a sample taskflow:

```
---
tasks:
  - source_data: "sample-resource"
    category: "azurecli"
    template: "sample-resource.create_group"
    output: "sample.txt"
```
Here ***data*** refers to a yml file that carries data to be injected into the template. ".yml" is not required in the name.

Data can be set in a couple of ways:
> Passing the entire yml file as the data (source).

Example:

```
data: "sample-resource"
```

> Passing a specific section of the data (source) file by setting the ***data_level***.

Example:

```
data: "sample-resource"
data_level: "sample>0"
```

***category*** refers to the folder in the templates folder.

***templates*** refers to a yml file that carries data to be injected into the template. ".yml" extension are not required for this.

***output*** refers to the generated output file from the template and the injected data.

### Setup Runners for Taskflows

- Use the "runner" folder to setup the list of taskflows you want to execute.
- Add the name of the taskflows you want to execute.
- Taskflows specified here are executed in linear order.

Below is an example of the same:
```
---
taskflows:
  - "sample-taskflow-8"
```


### Initiate the executor

> VOILA!

Setup Project for execution (assuming Mac, Ubuntu or WSL):

```
. ./cli_setup.sh
```

Execute the project:

```
zn run-all
```

If your environment uses *python3* to invoke python, change the cli_setup.sh like below:

```
alias zn='python3 main.py'
```

To view all available commands, type:
```
zn --help
```
