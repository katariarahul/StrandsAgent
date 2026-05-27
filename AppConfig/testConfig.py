from appconfig import get_runtime_config

config = get_runtime_config()

print("CONFIG CACHE:")
print(config['llm']['model_id'])