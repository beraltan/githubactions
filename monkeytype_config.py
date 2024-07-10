from monkeytype.config import DefaultConfig

class MyConfig(DefaultConfig):
    def python_paths(self):
        return ['src']

    def tracer(self):
        from monkeytype.tracing import CallTracer
        return CallTracer()

CONFIG = MyConfig()
