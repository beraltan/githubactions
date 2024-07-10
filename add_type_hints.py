import subprocess

# Step 1: Run your tests with MonkeyType tracing
subprocess.run(["monkeytype", "run", "test_example_module.py"])

# Step 2: Apply the generated type hints
subprocess.run(["monkeytype", "apply", "your_module_name"])
