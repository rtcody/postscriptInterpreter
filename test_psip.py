import pytest 
import main

def test_exch():
    main.op_stack.append(3)
    main.op_stack.append(4)
    main.exch
    assert main.op_stack.pop() == 4
    main.clear()

def test_div():
    main.op_stack.append(4)
    main.op_stack.append(2)
    main.div
    assert main.op_stack.pop() == 2
    main.clear()
    
def test_mul():
    main.op_stack.append(4)
    main.op_stack.append(2)
    main.mul()
    assert main.op_stack.pop() == 8
    main.clear()

def test_round():
    main.op_stack.append(4.7)
    main.round()
    assert main.op_stack.pop() == 5
    main.clear()

    main.op_stack.append(4.3)
    main.round()
    assert main.op_stack.pop() == 4
    main.clear()

def test_str_length():
    main.op_stack.append("hello world")
    main.str_length()
    assert main.op_stack.pop() == 11
    main.clear()

    main.op_stack.append("")
    main.str_length()
    assert main.op_stack.pop() == 0
    main.clear()

def test_eq():
    main.op_stack.append(3)
    main.op_stack.append(3)
    main.eq()
    assert main.op_stack.pop() == True
    main.clear()

    main.op_stack.append(3)
    main.op_stack.append(4)
    main.eq()
    assert main.op_stack.pop() == False
    main.clear()

def test_and_operation():
    main.op_stack.append(True)
    main.op_stack.append(False)
    main.and_operation()
    assert main.op_stack.pop() == False
    main.clear

    main.op_stack.append(True)
    main.op_stack.append(True)
    main.and_operation()
    assert main.op_stack.pop() == True
    main.clear()
    
if __name__ == "__main__":
    pytest.main(["-v", __file__])

