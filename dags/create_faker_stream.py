from kafka import KafkaProducer
import json, random, time
from faker import Faker

class FakerStream:
    @staticmethod
    def create_faker_stream(num_profiles):
        fake = Faker()
        profiles = []
        transactions = []

        # Generate profiles and transactions
        for _ in range(num_profiles):
            profile_uuid = str(fake.uuid4())

            profile = {
                'uuid': profile_uuid,
                'full_name': fake.name(),
                'email': fake.email(),
                'phone': fake.phone_number(),
                'address': fake.address(),
            }
            profiles.append(profile)

            # Generate transactions linked to the profile
            for _ in range(random.randint(1, 3)):
                transaction = {
                    'transaction_id': str(fake.uuid4()),
                    'profile_uuid': profile_uuid,
                    'amount': fake.random_int(min=1000, max=100000),
                    'transaction_date': str(fake.date_time_this_year()),  # Convert to string
                    'transaction_type': random.choice(['credit', 'debit'])
                }
                transactions.append(transaction)

        return {'profiles': profiles, 'transactions': transactions}

    @staticmethod
    def send_to_kafka(data):
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8')
        )

        for profile in data['profiles']:
            producer.send('faker', profile)
            time.sleep(0.1)
        
        for transaction in data['transactions']:
            producer.send('faker', transaction)
            time.sleep(0.1)
        
        producer.flush()

if __name__ == '__main__':
    data = FakerStream.create_faker_stream(1000)
    FakerStream.send_to_kafka(data)
