from datetime import datetime
import requests
import pathlib
import yaml
import sys
def getngnixlogs(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()
def get_inputs(filename):
    path = pathlib.Path(filename)
    if path.is_file():
        with path.open() as stream:
            if path.suffix == ".yaml" or path.suffix == ".yml":
                try:
                    vals = yaml.safe_load(stream)
                except yaml.scanner.ScannerError:
                    sys.exit(f"{filename} is not a proper YAML file")
    keys = vals.keys()
    if 'start_time' not in keys or 'end_time' not in keys or 'url' not in keys:
        sys.exit(f"{filename} does not have all the inputs. It should have start_time,end_time and url")
    return vals
def main():
    vals = get_inputs('input_example.yaml')
    error_status = vals['error_status']
    start_time = vals['start_time']
    end_time = vals['end_time']
    url = vals['url']
    lines = getngnixlogs(url)
    timestamp_format = "%d/%b/%Y:%H:%M:%S %z"
    try:
        start_time_ep = int(datetime.timestamp(datetime.strptime(start_time, timestamp_format)))
        end_time_ep = int(datetime.timestamp(datetime.strptime(end_time, timestamp_format)))
    except Exception as E:
        print(f"Provide timestamp in the required format {E}")
        exit(1)
    error_status_count = 0
    success_status_count = 0
    total_count = 0
    for line in lines:
        t = (line.split()[3][1:])
        o = (line.split()[4][:-1])
        timestamp = t + ' ' + o
        epoch = int(datetime.timestamp(datetime.strptime(timestamp, timestamp_format)))
        if start_time_ep <= epoch <= end_time_ep:
            total_count = total_count + 1
            if int(line.split()[8]) == error_status:
                error_status_count = error_status_count + 1
            elif int(line.split()[8]) == 200:
                success_status_count = success_status_count + 1
    error_percentage = (error_status_count / total_count) * 100
    success_percentage = (success_status_count / total_count) * 100
    print(
        f"The site has returned a total of {success_status_count} 200 responses, and {error_status_count} 404 "
        f"responses, out of total {total_count} requests between time {start_time} and time {end_time}")
    print(f"That is a {error_percentage} {error_status} errors, and {success_percentage} of 200 responses")
if __name__ == "__main__":
    main()

