import importlib
import traceback
import sys


def run():
    module = importlib.import_module('tests.test_main')
    tests = [
        getattr(module, name)
        for name in dir(module)
        if name.startswith('test_') and callable(getattr(module, name))
    ]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
        except Exception:
            failures += 1
            print(f"FAIL: {t.__name__}")
            traceback.print_exc()

    if failures:
        print(f"\n{failures} test(s) failed")
        sys.exit(1)
    else:
        print(f"\nAll {len(tests)} tests passed")
        sys.exit(0)


if __name__ == '__main__':
    run()
