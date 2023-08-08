from storages.backends.azure_storage import AzureStorage
import os


class AzureMediaStorage(AzureStorage):
    account_name = 'profilit'
    account_key = os.environ.get('azure_key')
    azure_container = 'media'
    expiration_secs = None


class AzureStaticStorage(AzureStorage):
    account_name = 'profilit'
    account_key = os.environ.get('azure_key')
    azure_container = 'static'
    expiration_secs = None
