def print_stream(stream, thinking=False):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

def display_stream(stream, thinking=False):
    for item in stream:
        if isinstance(item, tuple) and len(item) == 2:
            mode, s = item
        else:
            mode, s = "values", item
        if not thinking and mode != "values":
            continue
        try:
            message = s["messages"][-1]
        except (KeyError, IndexError, TypeError):
            print(item)
            continue
        if isinstance(message, tuple):
            print(message)
        else:
            try:
                content = message.content
                if isinstance(content, list) and len(content)>0:
                    if 'text' in content[0]:
                        print("================================== Ai Message ==================================\n")
                        print(content[0]['text'])
                else:
                    message.pretty_print()
            except AttributeError:
                print(message)