from zcore.secret.zaunic_service import ZaunicSecretsService

def Factory(service_name):
    secrets_services = {
        "zaunic" : ZaunicSecretsService
    }
    return secrets_services[service_name]()