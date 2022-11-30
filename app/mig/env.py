"""
sqlalchemy env
"""

import os
from importlib import import_module
from os import listdir
from os.path import join, isfile

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
from db import SQLALCHEMY_DATABASE_URL, Base

config = context.config


def search_model(model_dir="models"):
    """
    모델 검색
    """
    for file in listdir(model_dir):
        if isfile(join(model_dir, file)):
            import_module(f'{model_dir.replace(os.sep, ".")}.{file.replace(".py", "")}')
        else:
            if file != '__pycache__':
                search_model(join(model_dir, file))


search_model()

target_metadata = Base.metadata


def run_migrations_offline():
    """
        migrations offline
    """
    # url = config.get_main_option("sqlalchemy.url")
    url = SQLALCHEMY_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# pylint: disable=invalid-name, unused-argument
def include_object(obj, name, type_, reflected, compare_to):
    """
        스키마 구분
    """
    return not (type_ == 'table' and obj.schema != target_metadata.schema)


def run_migrations_online():
    """
    migrations online
    """
    con = config.get_section(config.config_ini_section)
    con['sqlalchemy.url'] = SQLALCHEMY_DATABASE_URL
    connectable = engine_from_config(
        con,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        conn = connection.execution_options(
            schema_translate_map={"tenant_schema": target_metadata.schema})

        context.configure(
            connection=conn, target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
            include_schemas=True,
            version_table_schema=target_metadata.schema,
            template_args={'schema': target_metadata.schema}
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
