from Singleton import Singleton

import sys
import re

class AzureWebhookParser(Singleton):
    def _init_singleton(self):
        pass

    def parse_webhook(self):
        raw = ' '.join(sys.argv[4:])
        match = re.search(r'"?C\s\d{4}-\d{4}"?', raw)
        if match:
            return match.group(0).strip('"')
        else:
            raise Exception("The change id cannot be read from the passed webhook body.")