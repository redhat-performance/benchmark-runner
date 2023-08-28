import re
import sys
import json

input_text = sys.stdin.read()

match = re.search(r'dashboard = <<EOT(.*?)\nEOT\n', input_text, re.DOTALL)
if match:
    extracted_content = match.group(1).strip()
    try:
        parsed_dict = json.loads(extracted_content)
        if not isinstance(parsed_dict, dict):
            raise ValueError("Extracted content is not a valid JSON dictionary.")
        print(extracted_content)  # Print the extracted content to stdout
    except json.JSONDecodeError:
        raise ValueError("Extracted content is not valid JSON.")
else:
    raise ValueError('Dashboard JSON content not found')

