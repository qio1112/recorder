import csv
import random
import string
from datetime import datetime, timedelta


def generate_random_string(length):
    characters = string.ascii_letters + string.digits  # Includes letters and digits
    random_string = ''.join(random.choice(characters) for i in range(length))
    return random_string


def csv_generator(num_rows=100):
    columns = ["date", "amount", "source", "destination", "type", "content", "person", "labels"]
    file_path = "test.csv"
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 9, 1)
    source_list = ["amex gold", "capital one", "discover", "chase", ""]
    destination_list = ["wells fargo checking", "amex saving", "chase saving", ""]
    type_list = ["income", "spend", "transfer", ""]
    person_list = ["dubdub", "lobo", ""]
    label_list = ["label1", "label2", "label3", "label4", "label5"]
    with open(file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(columns)
        for i in range(1000):
            date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
            date = date.strftime('%Y-%m-%d')
            amount = random.uniform(-1000, 10000)
            source = random.choice(source_list)
            destination = random.choice(destination_list)
            type = random.choice(type_list)
            content = generate_random_string(30)
            person = random.choice(person_list)
            num_labels_to_select = random.randint(0, 3)
            labels = "|".join(sorted(random.sample(label_list, num_labels_to_select)))
            line = [date, amount, source, destination, type, content, person, labels]
            csv_writer.writerow(line)
    return file_path








