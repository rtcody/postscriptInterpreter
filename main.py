import logging
logging.basicConfig(level=logging.INFO)
op_stack = []
dict_stack = [{}]  

#Scoping toggle
USE_LEXICAL_SCOPING = True

class ParseFailed(Exception):
    """ Exception while parsing """
    def __init__(self, message):
        super().__init__(message)

class TypeIsMismatch(Exception):
    """ Exception for type mismatch """
    def __init__(self, message):
        super().__init__(message)

def repl():
    global USE_LEXICAL_SCOPING
    
    if USE_LEXICAL_SCOPING:
        print("Lexical scoping is currently enabled.")
    else:
        print("Dynamic scoping is currently enabled.")
    
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
    
def process_string(input):
    logging.debug(f"Input to process string: {input}")
    if len(input) >= 2 and input.startswith("(") and input.endswith(")"):
        return input[1:-1]  # Return the string without parentheses
    else:
        raise ParseFailed("Can't parse this into a string")

PARSERS = [
    process_boolean,
    process_number,
    process_code_block,
    process_name_constants,
    process_string
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
            if USE_LEXICAL_SCOPING == True:
                dict_stack[-1][key] = value
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
dict_stack[-1]["="] = pop_and_print

def lookup_in_dictionary(input):
    if USE_LEXICAL_SCOPING:
       pass #Lexical scoping is not implemented yet
    else:
        for d in reversed(dict_stack):
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

#exch operation, swaps the top two elements of the stack
def exch():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation exch")
    op_stack[-1], op_stack[-2] = op_stack[-2], op_stack[-1]
dict_stack[-1]["exch"] = exch

#pop operation, removes the top element of the stack
def pop():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation pop")
    op_stack.pop()
dict_stack[-1]["pop"] = pop

#copy operation, copies the top n elements of the stack
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

#dup operation, duplicates the top element of the stack
def dup():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for dup")
    op_stack.append(op_stack[-1])
dict_stack[-1]["dup"] = dup

#clear operation, clears the stack
def clear():
    global op_stack
    op_stack = []
dict_stack[-1]["clear"] = clear

#count operation, counts the number of elements in the stack
def count():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation count")
    op_stack.append(len(op_stack))
dict_stack[-1]["count"] = count

#add operation, adds the top two elements of the stack
def add():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation add")
    op_stack.append(op_stack.pop() + op_stack.pop())
dict_stack[-1]["add"] = add

#sub operation, subtracts the top two elements of the stack
def sub():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation sub")
    op1 = op_stack.pop()
    op2 = op_stack.pop()
    op_stack.append(op2 - op1)
dict_stack[-1]["sub"] = sub

#div operation, divides the top two elements of the stack
def div():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation div")
    op1 = op_stack.pop()
    op2 = op_stack.pop()
    if op1 == 0:
        raise TypeIsMismatch("Division by zero")
    op_stack.append(op2 / op1)
dict_stack[-1]["div"] = div

#idiv operation, integer division of the top two elements of the stack
def idiv():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation idiv")
    op1 = op_stack.pop()
    op2 = op_stack.pop()
    if op1 == 0:
        raise TypeIsMismatch("Division by zero")
    op_stack.append(op2 // op1)
dict_stack[-1]["idiv"] = idiv

#mul operation, multiplies the top two elements of the stack
def mul():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation mul")
    op_stack.append(op_stack.pop() * op_stack.pop())
dict_stack[-1]["mul"] = mul

#mod operation, modulus of the top two elements of the stack
def mod():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation mod")
    op1 = op_stack.pop()
    op2 = op_stack.pop()
    if op1 == 0:
        raise TypeIsMismatch("Division by zero")
    op_stack.append(op2 % op1)
dict_stack[-1]["mod"] = mod

#neg operation, negates the top element of the stack
def neg():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation neg")
    op_stack.append(-op_stack.pop())
dict_stack[-1]["neg"] = neg

#ceiling operation, rounds up the top element of the stack
def ceiling():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation ceiling")
    op_stack.append(int(float(op_stack.pop() + 0.999999)))
dict_stack[-1]["ceiling"] = ceiling

#floor operation, rounds down the top element of the stack
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

#sqrt operation, calculates the square root of the top element of the stack
def sqrt():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation sqrt")
    op1 = op_stack.pop()
    if op1 < 0:
        raise TypeIsMismatch("Square root of negative number")
    op_stack.append(op1 ** .5)
dict_stack[-1]["sqrt"] = sqrt

#dict operation, creates a new dictionary of capacity n
def dict_operation():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation dict")
    n = op_stack.pop()
    if not isinstance(n, int) or n < 0:
        raise TypeIsMismatch("dict requires a non-negative integer")
    new_dict = {} 
    op_stack.append(new_dict) 
dict_stack[-1]["dict"] = dict_operation

#length operation, returns number of key value pairs in the dictionary
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

#maxlength operation, returns the maximum length of the elements in the stack
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

#begin operation, pushed a new dictionary onto the stack
def begin():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation begin")
    op1 = op_stack.pop()
    if isinstance(op1, dict):
        dict_stack.append(op1)
    else:
        raise TypeIsMismatch("begin requires a dictionary")
dict_stack[-1]["begin"] = begin

#end operation, pops the top dictionary off the stack
def end():
    if len(dict_stack) < 2:
        raise TypeIsMismatch("Not enough dictionaries to end")
    dict_stack.pop()
dict_stack[-1]["end"] = end

#string length operation, returns the length of the string
def str_length():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation str_length")
    op1 = op_stack.pop()
    if isinstance(op1, str):
        op_stack.append(len(op1))
    else:
        raise TypeIsMismatch("str_length requires a string")
dict_stack[-1]["str_length"] = str_length

#string get operation, returns the character at the given index
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

# string get interval operation, returns a substring from index to index plus count minus one
def str_get_interval():
    if len(op_stack) < 3:
        raise TypeIsMismatch("Not enough operands for operation str_get_interval")
    count = op_stack.pop()  
    index = op_stack.pop() 
    string = op_stack.pop()
    if isinstance(string, str) and isinstance(index, int) and isinstance(count, int):
        if 0 <= index and index + count <= len(string):
            op_stack.append(string[index:index + count])
        else:
            raise TypeIsMismatch("Index out of range")
    else:
        raise TypeIsMismatch("str_get_interval requires a string and two integer indices")
dict_stack[-1]["str_get_interval"] = str_get_interval

#string put operation, replaces the character at the given index with a new character
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

#eq operation, checks if the top two elements are equal
def eq():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation eq")
    op_stack.append(op_stack.pop() == op_stack.pop())
dict_stack[-1]["eq"] = eq

#ne operation, checks if the top two elements are not equal
def ne():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation ne")
    op_stack.append(op_stack.pop() != op_stack.pop())
dict_stack[-1]["ne"] = ne

#ge operation, checks if the first element is greater than or equal to the second
def ge():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation ge")
    op_stack.append(op_stack.pop() >= op_stack.pop())
dict_stack[-1]["ge"] = ge

#gt operation, checks if the first element is greater than the second
def gt():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation gt")
    op_stack.append(op_stack.pop() > op_stack.pop())
dict_stack[-1]["gt"] = gt

#le operation, checks if the first element is less than or equal to the second
def le():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation le")
    op_stack.append(op_stack.pop() <= op_stack.pop())
dict_stack[-1]["le"] = le

#lt operation, checks if the first element is less than the second
def lt():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation lt")
    op_stack.append(op_stack.pop() < op_stack.pop())
dict_stack[-1]["lt"] = lt

#and operation, checks if both elements are true
def and_operation():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation and")
    op_stack.append(op_stack.pop() and op_stack.pop())
dict_stack[-1]["and"] = and_operation

#not operation, checks if the top element is false
def not_operation():
    if len(op_stack) < 1:
        raise TypeIsMismatch("Not enough operands for operation not")
    op_stack.append(not op_stack.pop())
dict_stack[-1]["not"] = not_operation

#or operation, checks if either element is true
def or_operation():
    if len(op_stack) < 2:
        raise TypeIsMismatch("Not enough operands for operation or")
    op_stack.append(op_stack.pop() or op_stack.pop())
dict_stack[-1]["or"] = or_operation

#true operation, pushes true onto the stack
def true_operation():
    op_stack.append(True)
dict_stack[-1]["true"] = true_operation

#false operation, pushes false onto the stack
def flase_operation():
    op_stack.append(False)
dict_stack[-1]["false"] = flase_operation

#if operation, executes the block if the condition is true
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

#ifelse operation, executes the true block if the condition is true, else executes the false block
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

#while operation, executes the block while the condition is true
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

#repeat operation, executes the block a specified number of times
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