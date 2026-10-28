import os
from dotenv import dotenv_values

# Инициализация среды
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, ".env.secrets")
config = dotenv_values(dotenv_path)
# CONFIG_PATH = '/app/config/config.json'
print(config)

for i in config:
    print(i)