import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='session')

channel.basic_publish(exchange='', routing_key='session', body='Hello World!')
print('Sent Hello World!')
connection.close()
