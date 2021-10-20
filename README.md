# **Zaunic**
Configurable, easy-to-use accelerator.

![Zaunic](https://github.com/razaibi/zaunic/raw/main/project_assets/zaunic_logo_color.png)

## Environment Setup

- Ensure you using Windows Subsystem for Linux (WSL) or Ubuntu or any Debian based OS.
- Ensure you have Python 3 installed.
- Ensure you have Git installed.
- Clone this repository using:
```
git clone https://www.github.com/razaibi/zaunic
```

- Install dependencies using the below command:
```bash
pip install -r requirements.txt
```

- From the folder of the cloned repository, setup Project for execution (assuming Mac, Ubuntu or WSL) by running the below command:

```
. ./cli_setup.sh
```

# Quick Demo in 6 (mins) Guide:
This is demo to **generate** a file using a template and some data.
- Feed some data to demo template.
  * Let us navigate to the **demo-data.yml** file in the **data** folder.
  * It should look something like this. Replace **Your Name** with your name. Maintaining quotes is recommended.
```yaml
---
data:
  user_name: "Your Name"
```
- Now let us decide where to run this demo.
  * Navigate to **sample-nodes.yml** in the **nodes** folder and enter credentials of the node to run the demo on. Save your changes.

- Navigate to **running-list.yml** in the **runner** folder and ensure that **demo-taskflow** is part of the list.

- Voila! you are now ready to run the demo. From the project folder, run the below command:

```
zn run-all
```


# Detailed Implementation Guide

At a high level, the below checklist is a good starting point as your start implementing your taskflows.

![Implementation Checklist](https://github.com/razaibi/zaunic/raw/main/project_assets/implementation_checklist.png)

## **Node(s) Overview and Setup**

Folder Location: **data**
File format: **.yml**

Setting up nodes for execution. This is potentially the server on which you intend to execute the action. Behind the scenes there a connection that facilitates SSH and SFTP. 

Here is a brief explanation of the yaml structure and properties.

![Nodes YAML explanation](https://github.com/razaibi/zaunic/raw/main/project_assets/nodes_yaml_explanation.png)

Below is a sample node file for you to copy.
```yaml
---
nodes:
  - name: "Test Node"
    protocol: 'ssh'
    hostname: 'Your Host IP Address'
    connection_mode: "credentials"
    username: "XXXXXXXX"
    password: "XXXXXXXX"
```

Given the nature of the node files, ensure that Zaunic is hosted on a **secure server** with **RBAC**.

## **Taskflow(s) Overview and Setup**

Folder Location: **data**
File format: **.yml**

Taskflows are the over-arching abstractions that Zaunic uses for **managing tasks and tying them to actions**. Using task flows you can bundle a set of tasks, define their parameters and execute them.

**Tasks** are the most basic units in a Taskflow. The structure of Tasks is determined by their intended actions.

### Actions 

Broadly Actions are classified into the following types.

![Actions explanation](https://github.com/razaibi/zaunic/raw/main/project_assets/actions_explanation.png)

- Actions that **Generate content/data/files**.
- Actions that **Push content/data/files**.
- Actions that **Execute commands/scripts**.
- Actions that **Call APIs/endpoints**.

## **Defining Tasks**

Based on the type of actions, the tasks should following the below shown structure(s).

### **Upload Action**

```yaml
tasks:
  - name: "Upload File to Dev Server"
    action: "upload"
    source: "./upload_bay/transfer_file_sample.txt"
    destination: "/something/transfer_file_sample.txt"
```

  * **action** here specifies upload as you intend to upload content/files to server.
  * **source** refers to the local file which is intended to be uploaded.
  * **destination** is the destination to which the file needs to be transferred.

### **Execute Action**

```yaml
tasks:
  - name: "Run file on Dev Server"
    action: "execute"
    command: "curl https://example.org/ >> /something/site-code.html"
```

  * **action** here specifies execute action for the task.
  * **command** refers to the command you would like to execute from the shell.

### **Call API Action**

```yaml
tasks:
  - name: "Make a POST request"
    action: "call_rest_api"
    mode: remote
    request:
      url: 'https://reqbin.com/echo/post/json'
      method: 'POST'
      headers:
        Accept: application/json
      body:
        Id: 78912
        Customer: "Jason Sweet"
        Quantity: 1
        Price: 18.00
      return:
        status_code: 200
        type: json
      output: '/sample-post.json'
```

Ensure consistent indentation or copy the above snippet to avoid errors.

  * **action** here specifies call_rest_api action for the task.
  * **mode** here specifies if the call is supposed to be made on the conected node or the local machine where Zaunic is being run. If the mode is not specified, 'remote' is taken as default.
  * **url** is part of the request and refers to the endpoint url.
  * **method** is the name of the HTTP method(GET, POST, PUT, DELETE, PATCH) to use for the call.
  * **headers** is an optional part of the request and carries the query parameters to be be passed.
  * **params** is an optional part of the request and carries the query parameters to be be passed.
  * **body** is an optional part of the request and carries the query parameters to be be passed.
  * **return** defines what is the expected return format and status code.
  * **output** specifies what file to write the results to.



### **Generate Action**

```yaml
tasks:
  - name: "Show generation example."
    action: "generate"
    category: "bash"
    template: "print>secret"
    output: "/>something>secrets_demo.sh"
```

Ensure consistent indentation or copy the above snippet to avoid errors.

  * **action** here specifies the generate action for the task.
  * **category** refers to the **subfolder** of the templates folder.
  * **template** refers to actual file inside the *category* that is mentioned earlier.

Notice how the template value is **print>secret**. This is when you intend to use **Short Templates** or single line templates. Review the **Templates Setup** section below to see further details.

  * **output** refers to the location of the generated file. Notice how this is separated by **>** instead of the usual separation that you see in your file system. This separator is configurable in the **CONFIGS.py** file. **>** has been used to enhance readability. Behind the scenes, Zaunic takes care of making it palatable for the local file system.

### **Generate Action - Templates Types and Setup**

- In the templates folder, navigate to an **existing directory** or **create a new one**.
- Templates can be of two types:

> **Short Template** for single line or short templates that can be grouped together in one file. These are setup in a *.yml* file (for now). Below is an example of a couple of short templates from the sample *templates/azurecli/folder/sample-resource.yml*. 

```yaml
---
 create_group: "az group create --name {{ resource_group_name }} --location {{ location }}"
 update: "az update"

```

> **Long Template** for complex and long templates that require complete individual files. Below is an example of a long template from the sample *templates/postgresql/sample_ddl.j2*.

```jinja
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

> **Note how the formats for long and short templates are different (.yml vs .j2)**

## Using Secrets in Templates

In order to use secrets in a template, you can use the below format:

```jinja
{{secrets.<name_of_your_secret>}}
```

### **Generate Action - Source Data Setup**

Data source for the **task** can be set in a couple of ways:
> Passing the entire yml file as the data (source).

Example:
```yaml
data: "sample-resource"
```

> Passing a specific section of the data (source) file by setting the **data_level**.

Example:

```yaml
data: "sample-resource"
data_level: "sample>0"
```

To setup the actual source data file, navigate to the **data** folder and setup your **yml** file. Source data can be flat or nested. Below is an example from *sample-resource.yml* file from the *data* folder.

```yaml
---
data:
  sample:
    - location: south-central-us
      resource_group_name: sample-group
```

This data will be picked up by the task in your Taskflow and output will be generated. the schema of the data is **flexible** and can have multiple levels of nesting. Also the files created in the **data** folder can be used across tasks.

### **Generate Action - Secrets Management (Optional)**

Folder Location(s): 
- **secret_configs**
- **secretstore**

***CAUTION: Do not edit.***

Zaunic offers multiple ways to **impute secrets into templates**.

- Zaunic Secrets Management

This is credential management feature internal to Zaunic. Here credentials are first encrypted using an encryption key (called **global encryption key**) for respective environments (**dev, stage, pre-prod, prod**).

![Zaunic Secrets Explanation](https://github.com/razaibi/zaunic/raw/main/project_assets/zaunic_secrets_explanation.png)

In order to create a new secret, execute the below command:

```bash
zn add-secret --env=<dev> --name=<name of your secret> --val=<secret to encrypt>
```

- Cloud Base Secret Management

For Cloud based secret management, only required **client parameters** for accessing secrets are stored locally. The actual secret is stored in a Cloud Service Like Azure Key Vault, Google Secret Manager, Hashicorp Vault, etc.

**Client Parameters** here implies values such as **Client Id**, **Tenant Id**, **Client Secret**, **Subscription Id** depending upon the specific cloud provider.

In order to retrieve an actual secret from a Cloud Based Service, Zaunic is **highly prescriptive** about the nomenclature.

The client parameters (referred above) **should be encrypted and stored** in the the *Zaunic Secret Store* or as *environment variables*. The permitted format is as below.

For a client parameter liked **client_id**, a Zaunic secret/envrionment variable should be saved in the following format:

```bash
zn add-secret azure-<instance-of-service>-<environment>-<credential_type>
```

## Setup Runners for Taskflows

- Use the "runner" folder to setup the list of taskflows you want to execute.
- Add the name of the taskflows you want to execute.
- Taskflows specified here are executed in linear order.

Below is an example of the same:
```yaml
---
taskflows:
  - "sample-taskflow-8"
```

## Initiate the executor

Setup Project for execution (assuming Mac, Ubuntu or WSL):
```bash
. ./cli_setup.sh
```

If your environment uses *python3* to invoke python, change the **cli_setup.sh** like below:

```bash
alias zn='python3 main.py'
```

Execute the project:
```bash
zn run-all
```

To view all available commands, type:
```bash
zn --help
```



