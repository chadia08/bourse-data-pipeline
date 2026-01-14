import BVCscrap
import inspect

functions = [
    'getCours', 'getDividend', 'getIndex', 'getIndexRecap', 
    'getIntraday', 'getKeyIndicators', 'getPond', 'loadata'
]

print("--- Documentation BVCscrap ---")
for func_name in functions:
    if hasattr(BVCscrap, func_name):
        func = getattr(BVCscrap, func_name)
        print(f"\nFunction: {func_name}")
        print(f"Signature: {inspect.signature(func)}")
        if func.__doc__:
            print(f"Doc: {func.__doc__.strip()}")
        else:
            print("Doc: Pas de documentation")
