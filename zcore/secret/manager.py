from zcore.secret.zaunic_service import ZaunicSecretsService
from zcore.secret.azure_service import AzureSecretsService
from zcore.secret.orchestrator_service import OrchestratorService


def Factory(service_name):
    secrets_services = {
        "basic" : OrchestratorService,
        "zaunic" : ZaunicSecretsService,
        "azure" : AzureSecretsService
    }
    return secrets_services[service_name]()
