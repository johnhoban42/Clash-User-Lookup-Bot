# Raises an exception if something went wrong with fetching a JSON
class HttpError(Exception):

    def __init__(self, status_code, reason="", search_key=""):
        # This exception should not represent a successful search
        if status_code == 200:
            self.__del__()
        else:
            self.status_code = status_code
            self.reason = reason
            self.search_key = search_key

    # A brief explanation of the error, which will be sent to Discord for the user to see
    def __str__(self):
        return f"Could not fetch results for search key \"{self.search_key}\"\n" \
               f"HTTP Status Code: {self.status_code} ({self.reason})"

    def __del__(self):
        pass
