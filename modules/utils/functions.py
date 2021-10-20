from datetime import datetime


def time_diff_min(start_time: datetime, end_time: datetime = datetime.now()):
    '''Returns the distance between two Datetimes in minutes
    '''
    
    if start_time <= end_time:
        return round((end_time - start_time).total_seconds() / 60.0)
    return 0
