import json

# Read the config.json file
with open('config.json', 'r') as file:
    config_data = json.load(file)

# Modify the values
config_data['stopSignThreshold'] = 0.5  # Modify stopSignThreshold
config_data['trafficThreshold'] = 0.2  # Modify trafficThreshold
config_data['carThreshold'] = 0.1     # Modify carThreshold
config_data['yieldThreshold'] = 0.1   # Modify yieldThreshold
config_data['personThreshold'] = 0.8   # Modify personThreshold

# Save the modified data back to config.json
with open('config.json', 'w') as file:
    json.dump(config_data, file, indent=4)

print("config.json has been successfully updated!")
