import os

from datetime import datetime

def time_diff_min(start_time: datetime, end_time: datetime = datetime.now()):
    """Returns the distance between two Datetimes in minutes
    """
    
    if start_time <= end_time:
        return round((end_time - start_time).total_seconds() / 60.0)
    return 0


class Attach:
    """Construct a Attach for local files"""
    def __init__(self, filepath) -> None:
        self.filepath = filepath

    @property
    def filename(self):
        return self.filepath.split('/')[-1]
    
    @property
    def url(self):
        return 'attachment://' + self.filename
    
    @property
    def size(self):
        """Return file sixe to KB"""
        return round(
            number = os.path.getsize(self.filepath) / 1024, 
            ndigits=2
        )


