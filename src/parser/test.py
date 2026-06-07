import re

data = "nb_drones: 255645646"

nb = re.findall(r"-?\d+", data)
if len(nb) != 1:
    print("Invalid nb_drones format")
print(nb)