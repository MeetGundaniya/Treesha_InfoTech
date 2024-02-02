"""
RESTful API Client

This script allows users to make GET or POST requests to a specified API endpoint and provides options to handle the response data.
It supports saving the response data to either a JSON or CSV file.

Usage:
python ./restful.py [method] [endpoint] [-d data] [-o output]

Positional Arguments:
  method                Request method (choices: 'get', 'post')
  endpoint              Request endpoint URI fragment

Optional Arguments:
  -d, --data            Data to send with the request (must be a valid JSON string)
  -o, --output          Output to .json or .csv file (default: dump to stdout)
"""

import json
import requests
import argparse
from io import StringIO
from pprint import pprint
import pandas as pd


class Writer:
  """ Utility class for saving response data to different file formats.

  Attributes:
    dump_params (dict): Dictionary mapping file extensions to parameters for data dumping.
                        Currently supports 'json' and 'csv'.
  """

  # Dictionary to store parameters for different file formats when dumping data
  dump_params = {
    'json': {'orient': 'records', 'indent': 2},
    'csv': {},
    # 'html': {},
    # 'xml': {},
    # 'sql': {},
    # 'pkl': {},
    # 'xlsx': {}
  }


  def save(self, out_file: str, res_text):
    """ Save the response data to a file.

    Args:
      out_file (str): Output file path.
      res_text (str): Response data in text format.
    """

    # Convert API response text to Pandas.DataFrame
    df = pd.read_json(StringIO(res_text))

    # Extract file extension from output file path
    file_name,ext = out_file.rsplit('.', 1)

    # Check if dumping parameters are available for the specified file format
    if ext in self.dump_params:

      # Dynamically call the appropriate 'to_<format>' method on DataFrame
      getattr(df, f'to_{ext}')(f'{file_name}.{ext}', index=False, **self.dump_params[ext])

    else:
      print('not implemented for .{ext}')



class APITester(Writer):
  """ Class for testing RESTful API endpoints.

  Attributes:
    domain (str): Base domain for API requests.
    payload (dict): Payload containing request details (method, endpoint, data, output).
  """

  # Base domain for API requests
  domain = "https://jsonplaceholder.typicode.com"


  def __init__(self, payload:dict) -> None:
    """ Initialize the APITester instance with the provided payload.

    Args:
      payload (dict): Payload containing request details.
    """
    self.payload = payload

    # Construct the full URL for the API request
    url = f"{self.domain}/{self.payload['endpoint']}"

    try:
      # Dynamically call the appropriate API request based on specified method
      response = getattr(self, self.payload['method'])(url)

      print(f"status_code: {response.status_code}")
      response.raise_for_status() 

    except Exception as e:
      print(e)

    else:
      # If the response status code not success (2xx) then interrupt process
      if str(response.status_code)[0] != '2':
        raise Exception("Can't process non-success(2xx) request")

      # If the output file path given then Save the API response to the file,
      # Otherwise Pretty-print the response in JSON format
      output = self.payload.get('output', None)
      if output:
        res_text = response.text
        if response.text.startswith('{') and response.text.endswith('}'):
          res_text = f"[{response.text}]" 
        self.save(output, res_text)

      else:
        pprint(response.json())


  def get(self, url:str, **kwargs):
    """ Make a GET request to the specified URL.

    Args:
      url (str): URL to make the GET request.
      **kwargs: Additional keyword arguments for the request.

    Returns:
      requests.Response: Response object.
    """
    # Perform a GET request using the requests library
    return requests.get(url, **kwargs)


  def post(self, url:str, **kwargs):
    """ Make a POST request to the specified URL with JSON data.

    Args:
      url (str): URL to make the POST request.
      **kwargs: Additional keyword arguments for the request.

    Returns:
      requests.Response: Response object.
    """

    # Try to parse the 'data' field from the payload as JSON
    try:
      data = json.loads(self.payload.get('data', None))
    except TypeError as e:
      raise Exception("Must required valid json data")
    else:
      return requests.post(url, data=data, **kwargs)



def main():
  """
  Main function to handle command-line arguments and initiate the API testing.

  Raises:
    SystemExit: Exits with the corresponding exit code.
  """

  # Create an ArgumentParser for handling command-line arguments
  parser = argparse.ArgumentParser(description="RESTful API Client")

  # Positional arguments
  parser.add_argument('method', choices=['get' , 'post'], help='Request method')
  parser.add_argument('endpoint', help='Request endpoint URI fragment')

  # Optional arguments
  parser.add_argument('-d', '--data', help='Data to send with request')
  parser.add_argument('-o', '--output', default=None, help='Output to .json or .csv file (default: dump to stdout)')

  try:
    # Parse the command-line arguments and create an instance of APITester
    args = parser.parse_args()
    APITester(vars(args))

  except SystemExit as e:
    print(f"ExitCode:{e}    (-h for more info)")
    return

  except Exception as e:
    print(e)


if __name__ == '__main__':
  main()
