from zcore import core

def run_all():
    #core.process_template(
    #    "postgresql",
    #    "ddl",
    #    "db.yml"
    #)
    #core.process_playbook("playbook-1")
    core.run()

def main():
    run_all()

if __name__=='__main__':
    main()