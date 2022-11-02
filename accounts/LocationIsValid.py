import re
def checkLocation(x):
  y = x.replace(" ", "")
  locations = y.split(",")
  for location in locations:
        regx = re.match('[+-]?([0-9]*[.])?[0-9]+', location)
        if regx:
          if regx.group() == location:
            return True
          else:
            return False
