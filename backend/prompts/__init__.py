import yaml
from pathlib import Path

class PromptRegistry:
    def __init__(self):
        registry_path = Path(__file__).parent / "prompt_registry.yaml"
        if registry_path.exists():
            with open(registry_path) as f:
                self.registry = yaml.safe_load(f)
        else:
            self.registry = {}
    
    def get_prompt(self, prompt_type, version=None):
        """Get a prompt by type and version"""
        if prompt_type not in self.registry.get('prompts', {}):
            raise KeyError(f"Prompt type '{prompt_type}' not found in registry")
        
        if version is None:
            version = self.registry['prompts'][prompt_type].get('current_version', 'v1')
        
        if version not in self.registry['prompts'][prompt_type].get('versions', {}):
            raise KeyError(f"Prompt version '{version}' not found for '{prompt_type}'")
        
        file_name = self.registry['prompts'][prompt_type]['versions'][version]['file']
        file_path = Path(__file__).parent / file_name
        
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")
        
        with open(file_path) as f:
            return f.read()
    
    def set_current_version(self, prompt_type, version):
        """Switch to a different prompt version"""
        self.registry['prompts'][prompt_type]['current_version'] = version
        
        registry_path = Path(__file__).parent / "prompt_registry.yaml"
        with open(registry_path, 'w') as f:
            yaml.dump(self.registry, f)
        
        print(f"✅ Switched {prompt_type} to {version}")

prompt_registry = PromptRegistry()
