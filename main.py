import typer
from zcore import core
from zcore.secret.manager import Factory as SecretFactory

app = typer.Typer()


@app.command()
def run_all():
    #core.process_template(
    #    "postgresql",
    #    "ddl",
    #    "db.yml"
    #)
    #core.process_playbook("playbook-1")
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
        value: str = typer.Option(..., "--val", "--v"),
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
