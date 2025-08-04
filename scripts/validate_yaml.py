#!/usr/bin/env python3
import sys
import yaml

def validate_yaml(file_path):
    try:
        with open(file_path, 'r') as file:
            yaml_content = file.read()
            yaml.safe_load(yaml_content)
            print(f"✅ YAML file '{file_path}' is valid")
            return True
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error in '{file_path}':")
        print(e)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_yaml.py <path_to_yaml_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not validate_yaml(file_path):
        sys.exit(1)
