from django.conf import settings
from sqlalchemy import create_engine


def config():
    user = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    database_name = settings.DATABASES['default']['NAME']
    host = settings.DATABASES['default']['HOST']
    port = settings.DATABASES['default']['PORT']
    database_url = 'postgresql://{user}:{password}@{host}:{port}/{database_name}'.format(
        user=user,
        password=password,
        database_name=database_name,
        host=host,
        port=port
    )
    engine = create_engine(database_url)
    return engine
