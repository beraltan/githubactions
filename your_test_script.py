
import example

def test_example_function():
    assert example.example_function(1, 2) == 3
    assert example.example_function('a', 'b') == 'ab'

if __name__ == "__main__":
    test_example_function()
