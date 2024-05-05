import requests
import time
import jsonschema
import datetime
import statistics
import json
from jsonschema import validate


def load_schema(file_path):
    with open(file_path, 'r') as schema_file:
        return json.load(schema_file)


def send_requests(url, num_requests, delay, schema):
    sent = received = lost = 0
    round_trip_times = []

    for _ in range(num_requests):
        start_time = time.time()
        response = requests.get(url)
        sent += 1

        if response.status_code == 200 and is_json(response):
            received += 1
            req_time = time.time() - start_time
            round_trip_times.append(req_time)

            data = response.json()
            if is_valid_data(data, schema):
                print_save_result(response.status_code, data=data, is_json=True, valid_schema=True, req_time=req_time)
            else:
                print_save_result(response.status_code, data=data, is_json=True, valid_schema=False, req_time=req_time)
        else:
            lost += 1
            print_save_result(response.status_code)

        time.sleep(delay)

    return sent, received, lost, round_trip_times



def is_json(response):
    content_type = response.headers.get('content-type', '')
    return 'application/json' in content_type or 'application/vnd.orangeott.v1+json' in content_type


def is_valid_data(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError:
        return False


def print_save_result(status_code, req_time=-1, is_json=None, valid_schema=None, data=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = f'[{timestamp}] : request_time={req_time * 1000:.2f}ms;status_code={status_code}; is_json={is_json}; is_valid_schema={valid_schema}; data={data}\n'
    if status_code == 'Statistics':
        result = data
    print(result, end='')

    with open('log.txt', 'a') as file:
        file.write(result)


def print_statistics(sent, received, lost, round_trip_times):
    if received > 0:
        min_time = min(round_trip_times) * 1000
        max_time = max(round_trip_times) * 1000
        avg_time = statistics.mean(round_trip_times) * 1000

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = f'[{timestamp}] : Sent={sent}; Received={received}; Lost={lost}; Min RTT: {min_time:.2f} ms; Max RTT: {max_time:.2f} ms; Avg RTT: {avg_time:.2f} ms\n'
        print_save_result('Statistics', data=result)
    else:
        print("No responses received.")


def main():
    url = 'https://tvgo.orange.pl/gpapi/status'
    schema = load_schema('schema.js')
    num_requests = 3
    delay = 1

    sent, received, lost, round_trip_times = send_requests(url, num_requests, delay, schema)
    print_statistics(sent, received, lost, round_trip_times)


if __name__ == "__main__":
    main()

# polecenie ping jest wyłaczone dlatego wykonalem reczna implmentacje pakietow i ich czasow
# ponizej zamiescilem dzialajacy kod ktory wykonywal polecenie ping dla innego hosta
# from subprocess import PIPE, Popen
#
# host = "www.wp.pl"  # Change this to your desired host
# ping_count = 5
#
# data = ''
# output = Popen(f"ping {host} -n {ping_count}", stdout=PIPE, encoding="utf-8")
# i = 0
# for line in output.stdout:
#     print(f'{i} {line}')
#     i += 1
