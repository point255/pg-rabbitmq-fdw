from multicorn import ForeignDataWrapper
from multicorn.utils import log_to_postgres as log2pg

import logging
import pika


class RabbitmqFDW(ForeignDataWrapper):

    def __init__(self, options, columns):
        super(RabbitmqFDW, self).__init__(options, columns)

        self.host = options.get('host', 'localhost')
        self.port = int(options.get('port', '5672'))
        self.user = options.get('user', 'guest')
        self.password = options.get('password', 'guest')
        self.exchange = options.get('exchange', 'indexing')
        self.exchange_type = options.get('exchange_type', 'fanout')
        self.routing_key = options.get('routing_key', 'postgres')
        self._rowid_column = options.get('rowid_column', 'id')

        self.columns = columns

        # rabbitmq_parameters = pika.URLParameters('amqp://guest:guest@localhost:5672/%2F')
        self.rabbitmq_parameters = pika.URLParameters(
            'amqp://{0}:{1}@{2}:{3}/%2F'.format(self.user, self.password, self.host, self.port))

    @property
    def rowid_column(self):
        """ Returns a column name which will act as a rowid column for
            delete/update operations.
            This can be either an existing column name, or a made-up one. This
            column name should be subsequently present in every returned
            resultset. """

        return self._rowid_column

    # noinspection PyMethodMayBeStatic
    def execute(self, quals, columns, **kwargs):
        """ Should Execute the query but we don't handle it (for now?)"""

        log2pg("SELECT isn't implemented for RabbitMQ", logging.ERROR)
        yield {0, 0}

    def insert(self, new_values):
        """ Publish a new / updated / deleted document into RabbitMQ """

        log2pg('MARK Request - new values:  %s' % new_values, logging.DEBUG)

        if not ('table' in new_values):
            log2pg('It requires "table" column. Missing in: %s' % new_values, logging.ERROR)

        if not ('id' in new_values):
            log2pg('It requires "id" column. Missing in: %s' % new_values, logging.ERROR)

        if not ('action' in new_values):
            log2pg('It requires "action" column. Missing in: %s' % new_values, logging.ERROR)

        return self.rabbitmq_publish(new_values)

    def update(self, oldvalues, newvalues):
        log2pg("UPDATE isn't implemented for RabbitMQ", logging.ERROR)

    def delete(self, oldvalues):
        log2pg("DELETE isn't implemented for RabbitMQ", logging.ERROR)

    @classmethod
    def import_schema(cls, schema, srv_options, options, restriction_type, restricts):
        log2pg("IMPORT_SCHEMA isn't implemented for RabbitMQ", logging.ERROR)

    def rabbitmq_publish(self, values):
        """ Publish a message in RabbitMQ exchange """

        connection = pika.BlockingConnection(self.rabbitmq_parameters)
        channel = connection.channel()
        channel.exchange_declare(
            exchange=self.exchange,
            exchange_type=self.exchange_type,
            durable=True)

        channel.basic_publish(
            self.exchange,
            self.routing_key,
            '',
            pika.BasicProperties(
                delivery_mode=2,
                headers=values
            )
        )

        connection.close()
