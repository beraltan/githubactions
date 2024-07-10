from monkeytype.config import DefaultConfig

class MyConfig(DefaultConfig):
    def trace_module(self, module_name: str) -> bool:
        # Trace only modules in the src package
        return module_name.startswith('src.')

    def python_paths(self):
        return ['src']

CONFIG = MyConfig()
