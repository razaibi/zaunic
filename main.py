from yaml.nodes import Node
import typer
from zcore import core
from zcore.secret.manager import Factory as SecretFactory
from zcore.node import Manager as NodeManager

app = typer.Typer()


@app.command()
def run_all():
    #core.process_template(
    #    "postgresql",
    #    "ddl",
    #    "db.yml"
    #)
    #core.process_taskflow("taskflow-1")
    core.run()
    # Test Secret Management
    ## Add a secret called "client_id" to the dev environment.
    #sm = secret.Manager()
    #(Optional)
    #sm.set_global_encryption_key('dev')
    #sm.add_secret('dev','client_id', 'S0m#$up@_!n2erest!ng$*cre7')
    #sm.get_secret('dev','client_id')

@app.command()
def add_secret(
        env: str = typer.Option(..., "--env", "--e"),
        name: str = typer.Option(..., "--name", "--n"),
        value: str = typer.Option(
            ..., 
            "--val", 
            "--v", 
            prompt=True,
            confirmation_prompt=False, 
            hide_input=True
        ),
    ):
    secrets_service = SecretFactory("zaunic")
    secrets_service.set_secret(env, name, value)
    #sm.set_global_encryption_key(env)
    secrets_service.get_local_secret(env, name)

@app.command()
def get_secret(
        env: str = typer.Option(..., "--env", "--e"),
        name: str = typer.Option(..., "--name", "--n")
    ):
    secrets_service = SecretFactory("zaunic")
    secrets_service.get_secret(env, name)


@app.command()
def add_node(
        group: str = typer.Option(..., "--grp", "--g"),
        name: str = typer.Option(..., "--name", "--n"),
        host: str = typer.Option(..., "--host", "--h"),
        username: str = typer.Option(
            ..., 
            "--user", 
            "--u", 
            prompt=True,
            confirmation_prompt=False, 
            hide_input=True
        ),
        password: str = typer.Option(
            ..., 
            "--pass", 
            "--p", 
            prompt=True,
            confirmation_prompt=False, 
            hide_input=True
        )
    ):
    nm = NodeManager()
    nm.add_node_with_credentials(
        group,
        name,
        host,
        username.encode(),
        password.encode()
    )

@app.command()
def update_node(
        group: str = typer.Option(..., "--grp", "--g"),
        name: str = typer.Option(..., "--name", "--n"),
        host: str = typer.Option(..., "--host", "--h"),
        username: str = typer.Option(
            ..., 
            "--user", 
            "--u", 
            prompt=True,
            confirmation_prompt=False, 
            hide_input=True
        ),
        password: str = typer.Option(
            ..., 
            "--pass", 
            "--p", 
            prompt=True,
            confirmation_prompt=False, 
            hide_input=True
        )
    ):
    nm = NodeManager()
    nm.update_node_by_name(
        group,
        name,
        host,
        username.encode(),
        password.encode()
    )

@app.command()
def generate_node_key():
    """
    Generates the key that encrypts connection credentials for nodes.
    """
    nm = NodeManager()
    nm.generate_encryption_key()

@app.command()
def get_azure_secret(
        env: str = typer.Option(..., "--env", "--e"),
        name: str = typer.Option(..., "--name", "--n"),
        vault: str = typer.Option(..., "--vlt", "--v"),
    ):
    secrets_service = SecretFactory("zaunic")
    secret_struct = {
        'instance': vault,
        'env': env,
        'keyname' : name
    }
    secrets_service.get_azure_key_vault_secret(secret_struct)

if __name__ == "__main__":
    app()
