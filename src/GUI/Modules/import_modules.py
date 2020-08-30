import os
import sys
import importlib
import GUI.Modules
import warnings


def load_modules(name, modules_path=None, output_func=None):
    import_errors = []

    module_list = name.split('.')
    if name[-1] != '.':
        name += '.'

    if modules_path is None:
        modules_path = os.path.dirname(sys.argv[0])
        # modules_path = os.path.dirname(os.path.abspath(__file__))

    sys.path.append(modules_path)

    for m in module_list:
        modules_path = os.path.join(modules_path, m)

    menu_entry_loads = []
    menu_entry_loads_name = []
    # other_module_loads = []

    for subdir, dirs, files in os.walk(modules_path):
        # TODO: may want to use this as I think it will be fast (aka already 'compiled')
        if subdir.endswith('__pycache__'):
            continue

        current_module = name
        subdir = subdir.replace(modules_path, '')

        for d in subdir.split(os.path.sep):
            if d != '' and d != os.path.sep:
                current_module += d + '.'

        for file_name in files:

            if file_name == 'peak_pair.py':
                pass

            module_name = os.path.splitext(file_name)[0]

            if output_func is not None:
                output_func("Searching " + current_module + module_name)

            try:
                module = importlib.import_module(current_module + module_name)
            except ImportError as e:
                error_string = f'Could not load {current_module}{module_name}:\n {str(e)}'
                import_errors.append(error_string)
                warnings.warn(error_string)
                continue

            md = module.__dict__
            classes = [v for c, v in md.items() if (isinstance(v, type) and v.__module__ == module.__name__)]

            for cls in classes:
                if issubclass(cls, GUI.Modules.Module) and not cls == GUI.Modules.Module and not cls == GUI.Modules.MenuModule and not cls == GUI.Modules.MenuEntryModule:
                    # if issubclass(cls, MenuEntryModule):
                    menu_entry_loads.append(cls())
                    menu_entry_loads_name.append(current_module + module_name)

    # for now we can just install everything in one sorted list as we
    # only have one type of module that need to be ordered
    menu_entry_loads.sort(key=lambda x: x.order_priority, reverse=False)
    for m, mn in zip(menu_entry_loads, menu_entry_loads_name):
        if output_func is not None:
            output_func("Installing " + mn)
        try:
            m.install()
        except Exception as e:
            error_string = f'Could not load {mn}:\n {str(e)}'
            import_errors.append(error_string)
            warnings.warn(error_string)

    return import_errors
