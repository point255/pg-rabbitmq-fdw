""" Install file for Postgres Elasticsearch Foreign Data Wrapper """
from setuptools import setup

if __name__ == '__main__':
    setup(
        name='pg_rabbitmq',
        description='PostgreSQL RabbitMQ Foreign Data Wrapper (write only)',
        version='1.1.0',
        author='point255',
        license='MIT',
        packages=['pg_rabbitmq'],
        url='https://github.com/point255/pg-rabbitmq-fdw',
        test_suite="tests"
    )
