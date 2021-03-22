import json

with open('test_config.json', 'r') as f:
    config = json.load(f)
config['MIN'] = 1
with open('test_config.json', 'w') as f:
    json.dump(config, f, indent=4)