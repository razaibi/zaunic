import typer
from zcore import core
from zcore import secret

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
def hello(name: str = typer.Option(..., "--name", "--n")):
    typer.echo(f"Hello {name}")

@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        typer.echo(f"Goodbye Ms. {name}. Have a good day.")
    else:
        typer.echo(f"Bye {name}!")

if __name__ == "__main__":
    app()