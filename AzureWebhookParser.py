import sys
import re

class ApiService(Singleton):
    def parse_webhook_data(self):
        raw = ' '.join(sys.argv[4:])
        match = re.search(r'"?C\s\d{4}-\d{4}"?', raw)
        if match:
            return match.group(0).strip('"')
        else:
            return None