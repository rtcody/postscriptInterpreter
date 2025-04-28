import logging
logging.basicConfig(level=logging.INFO)
op_stack = []
dict_stack = [{}]  # Directly initializing instead of appending later

class ParseFailed(Exception):
    """ Exception while parsing """
    def __init__(self, message):
        super().__init__(message)

class TypeIsMismatch(Exception):
    """ Exception for type mismatch """
    def __init__(self, message):
        super().__init__(message)

def repl():
    while True:
        user_input = input("REPL> ")
        if user_input.lower() == "quit":
            break
        process_input(user_input)
        logging.debug(f"Operand Stack: {op_stack}")

def process_boolean(input):
    logging.debug(f"Input to process boolean: {input}")
    if input == "true":
        return True
    elif input == "false":
        return False
    else:
        raise ParseFailed("Can't parse it into boolean")

def process_number(input):
    logging.debug(f"Input to process number: {input}")
    try:
        float_value = float(input)
        if float_value.is_integer():
            return int(float_value)
        else:
            return float_value
    except ValueError:
        raise ParseFailed("Can't parse this into a number")

def process_code_block(input):
    logging.debug(f"Input to process code block: {input}")
    if len(input) >= 2 and input.startswith("{") and input.endswith("}"):
        return input[1:-1].strip().split()
    else:
        raise ParseFailed("Can't parse this into a code block")

def process_name_constants(input):
    logging.debug(f"Input to process name constants: {input}")
    if input.startswith("/"):
        return input
    else:
        raise ParseFailed("Can't parse into name constants")

PARSERS = [
    process_boolean,
    process_number,
    process_code_block,
    process_name_constants
]

def process_constants(input):
    for parser in PARSERS:
        try:
            res = parser(input)
            op_stack.append(res)
            return
        except ParseFailed as e:
            logging.debug(e)
            continue
    raise ParseFailed(f"None of the parsers worked for the input {input}")

def add_operation():
    if len(op_stack) >= 2:
        op1 = op_stack.pop()
        op2 = op_stack.pop()
        res = op1 + op2
        op_stack.append(res)
    else:
        raise TypeIsMismatch("Not enough operands for operation add")

dict_stack[-1]["add"] = add_operation

def def_operation():
    if len(op_stack) >= 2:
        value = op_stack.pop()
        name = op_stack.pop()
        if isinstance(name, str) and name.startswith("/"):
            key = name[1:]
            dict_stack[-1][key] = value
        else:
            raise TypeIsMismatch("Name constant must start with '/'")
    else:
        raise TypeIsMismatch("Not enough operands for operation def")

dict_stack[-1]["def"] = def_operation

def pop_and_print():
    if len(op_stack) >= 1:
        op1 = op_stack.pop()
        print(op1)
    else:
        raise TypeIsMismatch("Stack is empty! Nothing to print")

# Add pop_and_print to the dictionary
dict_stack[-1]["print"] = pop_and_print

def lookup_in_dictionary(input):
    for d in reversed(dict_stack):  # Search from top to bottom
        if input in d:
            value = d[input]
            if callable(value):
                value()
            elif isinstance(value, list):
                for item in value:
                    process_input(item)
            else:
                op_stack.append(value)
            return
    raise ParseFailed(f"Input {input} is not in dictionary")

def process_input(user_input):
    try:
        process_constants(user_input)
    except ParseFailed as e:
        logging.debug(e)
        try:
            lookup_in_dictionary(user_input)
        except Exception as e:
            logging.exception(e)

def exch():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation exch")
    op_stack[-1], op_stack[-2] = op_stack[-2], op_stack[-1]
dict_stack[-1]["exch"] = exch

def pop():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation pop")
    op_stack.pop()
dict_stack[-1]["pop"] = pop

def copy():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation copy")
    n = op_stack.pop()
    if not isinstance(n, int) or n < 0:
        raise TypeIsMismatch("copy requires a non-negative integer")
    if len(op_stack) < n:
        raise TypeIsMismatch(f"Not enough operands for copying {n} elements")
    op_stack.extend(op_stack[-n:])
dict_stack[-1]["copy"] = copy

def dup():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation dup")
    op_stack.append(op_stack[-1])
dict_stack[-1]["dup"] = dup

def clear():
    global op_stack
    op_stack = []
dict_stack[-1]["clear"] = clear

def count():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation count")
    op_stack.append(len(op_stack))
dict_stack[-1]["count"] = count

def add():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation add")
    op_stack.append(op_stack.pop() + op_stack.pop())
dict_stack[-1]["add"] = add

def sub():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation sub")
    op1 = op_stack.pop()
    op2 = op_stack.pop()
    op_stack.append(op2 - op1)
dict_stack[-1]["sub"] = sub

def div():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation div")
    op1 = op_stack.pop()
    op2 = op_stack.pop()
    if op1 == 0:
        raise TypeIsMismatch("Division by zero")
    op_stack.append(op2 / op1)
dict_stack[-1]["div"] = div

def idiv():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation idiv")
    op1 = op_stack.pop()
    op2 = op_stack.pop()
    if op1 == 0:
        raise TypeIsMismatch("Division by zero")
    op_stack.append(op2 // op1)
dict_stack[-1]["idiv"] = idiv

def mul():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation mul")
    op_stack.append(op_stack.pop() * op_stack.pop())
dict_stack[-1]["mul"] = mul

def mod():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation mod")
    op1 = op_stack.pop()
    op2 = op_stack.pop()
    if op1 == 0:
        raise TypeIsMismatch("Division by zero")
    op_stack.append(op2 % op1)
dict_stack[-1]["mod"] = mod

def neg():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation neg")
    op_stack.append(-op_stack.pop())
dict_stack[-1]["neg"] = neg

def ceiling():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation ceiling")
    op_stack.append(int(float(op_stack.pop() + 0.999999)))
dict_stack[-1]["ceiling"] = ceiling

def floor():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation floor")
    op_stack.append(int(float(op_stack.pop())))
dict_stack[-1]["floor"] = floor

def round():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation round")
    op_stack.append( int(float(op_stack.pop() + 0.5)))
dict_stack[-1]["round"] = round

def sqrt():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation sqrt")
    op1 = op_stack.pop()
    if op1 < 0:
        raise TypeIsMismatch("Square root of negative number")
    op_stack.append(op1 ** .5)
dict_stack[-1]["sqrt"] = sqrt

def dict():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation dict")
    n = op_stack.pop()
    if not isinstance(n, int) or n < 0:
        raise TypeIsMismatch("dict requires a non-negative integer")
    new_dict = {}
    dict_stack.append(new_dict)
    op_stack.append(new_dict)
dict_stack[-1]["dict"] = dict

def length():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation length")
    op1 = op_stack.pop()
    if isinstance(op1, list):
        op_stack.append(len(op1))
    elif isinstance(op1, str):
        op_stack.append(len(op1))
    elif isinstance(op1, dict):  # Added support for dictionaries
        op_stack.append(len(op1))
    else:
        raise TypeIsMismatch("length requires a list, string, or dictionary")
dict_stack[-1]["length"] = length

def maxlength():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation maxlength")
    op1 = op_stack.pop()
    if isinstance(op1, dict):
        op_stack.append(len(op1))  # Just push once
    elif isinstance(op1, list) or isinstance(op1, str):
        op_stack.append(len(op1))
    else:
        raise TypeIsMismatch("maxlength requires a dictionary, list or string")
dict_stack[-1]["maxlength"] = maxlength

def begin():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation begin")
    op1 = op_stack.pop()
    if isinstance(op1, dict):
        dict_stack.append(op1)
    else:
        raise TypeIsMismatch("begin requires a dictionary")
dict_stack[-1]["begin"] = begin

def end():
    if len(dict_stack) < 2:
        raise TypeIsMismatch("Not enough dictionaries to end")
    dict_stack.pop()
dict_stack[-1]["end"] = end

def str_length():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation str_length")
    op1 = op_stack.pop()
    if isinstance(op1, str):
        op_stack.append(len(op1))
    else:
        raise TypeIsMismatch("str_length requires a string")
dict_stack[-1]["str_length"] = str_length

def str_get():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation str_get")
    index = op_stack.pop()
    string = op_stack.pop()
    if isinstance(string, str) and isinstance(index, int):
        if 0 <= index < len(string):
            op_stack.append(string[index])
        else:
            raise TypeIsMismatch("Index out of range")
    else:
        raise TypeIsMismatch("str_get requires a string and an integer index")
dict_stack[-1]["str_get"] = str_get

def str_get_interval():
    if len(op_stack) < 3:
        raise TypeIsMismatch("Not enough operands for operation str_get_interval")
    end = op_stack.pop()
    start = op_stack.pop()
    string = op_stack.pop()
    if isinstance(string, str) and isinstance(start, int) and isinstance(end, int):
        if 0 <= start <= end <= len(string):
            op_stack.append(string[start:end])
        else:
            raise TypeIsMismatch("Index out of range")
    else:
        raise TypeIsMismatch("str_get_interval requires a string and two integer indices")
dict_stack[-1]["str_get_interval"] = str_get_interval

def str_put_interval():
    if len(op_stack) < 3:
        raise TypeIsMismatch("Not enough operands for operation str_put_interval")
    new_string = op_stack.pop()
    start = op_stack.pop()
    string = op_stack.pop()
    if isinstance(string, str) and isinstance(start, int) and isinstance(new_string, str):
        if 0 <= start <= len(string):
            op_stack.append(string[:start] + new_string + string[start:])
        else:
            raise TypeIsMismatch("Index out of range")
    else:
        raise TypeIsMismatch("str_put_interval requires a string and an integer index")
dict_stack[-1]["str_put_interval"] = str_put_interval

def eq():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation eq")
    op_stack.append(op_stack.pop() == op_stack.pop())
dict_stack[-1]["eq"] = eq

def ne():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation ne")
    op_stack.append(op_stack.pop() != op_stack.pop())
dict_stack[-1]["ne"] = ne

def ge():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation ge")
    op_stack.append(op_stack.pop() >= op_stack.pop())
dict_stack[-1]["ge"] = ge

def gt():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation gt")
    op_stack.append(op_stack.pop() > op_stack.pop())
dict_stack[-1]["gt"] = gt

def le():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation le")
    op_stack.append(op_stack.pop() <= op_stack.pop())
dict_stack[-1]["le"] = le

def lt():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation lt")
    op_stack.append(op_stack.pop() < op_stack.pop())
dict_stack[-1]["lt"] = lt

def and_operation():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation and")
    op_stack.append(op_stack.pop() and op_stack.pop())
dict_stack[-1]["and"] = and_operation

def not_operation():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation not")
    op_stack.append(not op_stack.pop())
dict_stack[-1]["not"] = not_operation

def or_operation():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation or")
    op_stack.append(op_stack.pop() or op_stack.pop())
dict_stack[-1]["or"] = or_operation

def true_operation():
    op_stack.append(True)
dict_stack[-1]["true"] = true_operation

def flase_operation():
    op_stack.append(False)
dict_stack[-1]["false"] = flase_operation

def if_operation():
    if len(op_stack) < 3:
        raise TypeIsMismatch("Not enough operands for operation if")
    else:
        condition = op_stack.pop()
        true_block = op_stack.pop()
        false_block = op_stack.pop()
        if condition:
            process_input(true_block)
        else:
            process_input(false_block)
dict_stack[-1]["if"] = if_operation

def ifelse_operation():
    if len(op_stack) < 3:
        raise TypeIsMismatch("Not enough operands for operation ifelse")
    else:
        condition = op_stack.pop()
        true_block = op_stack.pop()
        false_block = op_stack.pop()
        if condition:
            process_input(true_block)
        else:
            process_input(false_block)
dict_stack[-1]["ifelse"] = ifelse_operation

def for_operation():
    if len(op_stack) < 4:
        raise TypeIsMismatch("Not enough operands for operation for")
    else:
        end = op_stack.pop()
        start = op_stack.pop()
        step = op_stack.pop()
        block = op_stack.pop()
        if isinstance(start, int) and isinstance(end, int) and isinstance(step, int):
            for i in range(start, end, step):
                process_input(block)
        else:
            raise TypeIsMismatch("for requires integers for start, end, and step")
dict_stack[-1]["for"] = for_operation

def repeat_operation():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation repeat")
    else:
        count = op_stack.pop()
        block = op_stack.pop()
        if isinstance(count, int):
            for _ in range(count):
                process_input(block)
        else:
            raise TypeIsMismatch("repeat requires an integer count")
dict_stack[-1]["repeat"] = repeat_operation

if __name__ == "__main__":
    repl()