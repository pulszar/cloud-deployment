# Source - https://stackoverflow.com/a/15940301
# Posted by Artsiom Rudzenka, modified by community. See post 'Timeline' for change history
# Retrieved 2026-09-13, License - CC BY-SA 4.0

from datetime import datetime, timezone
print(datetime.now(timezone.utc))
print(datetime.now(timezone.utc).timestamp() * 1000) # POSIX timestamp in milliseconds

print(datetime.now(timezone.utc).replace(tzinfo=None))
