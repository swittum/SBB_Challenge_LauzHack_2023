from dateutil import parser

def format_time(timestamp):
    parsed_timestamp = parser.parse(timestamp)
    hours = parsed_timestamp.hour
    minutes = parsed_timestamp.minute
    formatted_time = f"{hours:02}:{minutes:02}"
    return formatted_time