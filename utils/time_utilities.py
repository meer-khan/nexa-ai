from datetime import datetime , timezone
import pytz
# Define Pakistan Standard Time (PST) timezone
pst = pytz.timezone("Asia/Karachi")


# Convert PST time to UTC
def convert_pst_to_utc(pst_time: datetime) -> datetime:
    pst_localized = pst.localize(pst_time)
    return pst_localized.astimezone(timezone.utc)


def convert_utc_to_pst(utc_time: datetime):
    
    # Make sure the input time is aware (has timezone info). If not, add UTC tzinfo.
    if utc_time.tzinfo is None:
        utc_time = pytz.utc.localize(utc_time)
    
    # Define the target timezone (Asia/Karachi)
    pst_timezone = pytz.timezone("Asia/Karachi")
    
    # Convert UTC time to the specified timezone (PST in this case)
    pst_time = utc_time.astimezone(pst_timezone)
    
    return pst_time