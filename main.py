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

if __name__ == "__main__":
    app()
