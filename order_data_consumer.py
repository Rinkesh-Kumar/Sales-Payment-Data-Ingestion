import json
from google.cloud import pubsub_v1
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Initialize the Pub/Sub subscriber client
subscriber = pubsub_v1.SubscriberClient()

# Project and Topic details
project_id = "dataengineeringxxxxx9"
subscription_name = "orders_data-sub"
subscription_path = subscriber.subscription_path(project_id, subscription_name)

def cassandra_connection():
    cloud_config= {'secure_connect_bundle': r"Projects\Sales Order & Payment Data Real Time Ingestion\Cred\secure-connect-ecom-data.zip"}

    with open(r"Projects\Sales Order & Payment Data Real Time Ingestion\Cred\ecom_data-token.json") as f:
        secrets = json.load(f)

    CLIENT_ID = secrets["clientId"]
    CLIENT_SECRET = secrets["secret"]

    auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    
    session = cluster.connect('ecom_tranx')

    return cluster,session

# Setup Cassandra connection

cluster,session = cassandra_connection()

# Prepare the Cassandra insertion statement
insert_stmt = session.prepare("""
    INSERT INTO orders_payments_facts (order_id, customer_id, item, quantity, price, shipping_address, order_status, creation_date, payment_id, payment_method, card_last_four, payment_status, payment_datetime)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""")

# Pull and process messages
def pull_messages():
    while True:
        response = subscriber.pull(request={"subscription": subscription_path, "max_messages": 10})
        ack_ids = []

        for received_message in response.received_messages:
            # Extract JSON data
            json_data = received_message.message.data.decode('utf-8')
            
            # Deserialize the JSON data
            deserialized_data = json.loads(json_data)

            print(deserialized_data)
            
            # Prepare data for Cassandra insertion
            cassandra_data = (
                deserialized_data.get("order_id"),
                deserialized_data.get("customer_id"),
                deserialized_data.get("item"),
                deserialized_data.get("quantity"),
                deserialized_data.get("price"),
                deserialized_data.get("shipping_address"),
                deserialized_data.get("order_status"),
                deserialized_data.get("creation_date"),
                None,
                None,
                None,
                None,
                None
            )
            
            # Insert data into Cassandra
            session.execute(insert_stmt, cassandra_data)

            print("Data inserted in cassandra !!")
            
            # Collect ack ID for acknowledgment
            ack_ids.append(received_message.ack_id)

        # Acknowledge the messages so they won't be sent again
        if ack_ids:
            subscriber.acknowledge(request={"subscription": subscription_path, "ack_ids": ack_ids})

# Run the consumer
if __name__ == "__main__":
    try:
        pull_messages()
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up any resources
        cluster.shutdown()
