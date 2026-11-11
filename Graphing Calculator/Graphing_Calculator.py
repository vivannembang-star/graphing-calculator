#with my last attempt of a graphing calculator, i coded it in a way where i couldn't add components without destoying the entire system
#my main issues with my prototype was it did not have implicit multiplication, complex functions like trig, decimals, constants, and asympototes would crash the program
#what i did like was i coded my own tokenizer helping me avoid using eval which could run harmful code if entered. 



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

functions = []
domain = [-10, 10]

# here i import the library math to gain access to complex functions and constants, i store them in a dictionary where i can call them in the tokenizer i will build
import math
FUNCTIONS = {"sin": math.sin, "cos": math.cos, "tan": math.tan, 
             "sqrt": math.sqrt, "log": math.log10, "ln": math.log,
             "abs": abs}
CONSTANTS = {"pi": math.pi, "e": math.e}
PREC = {"+": 1, "-": 1, "*": 2, "/": 2, "neg": 2.5, "^": 3}
OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
       "*": lambda a, b: a*b, "/": lambda a, b: a/b, "^": math.pow}
# i also decide to pair operations with functions i define using lambda, i was thinking of trying to use def for each one which i did initally, however, was very inefficient, thinking about time and space complexity.
# giving each operation a precedence will allow me to use order of priority to order the way i solve things regarding my evaluator - shunting yard algorithm



# i'll start with the tokenizer, then move onto the evaluator. I'm not sure how i'll incorporate imiplicit multipliation yet, however, the idea of defining a new function for implicit multiplication seems like a better idea.
# trying to incorporate implicit multiplication in my tokenizer would make my code complex and difficult to read
def tokenize(text):
    text = text.replace(" ", "").lower()
    names = sorted(list(FUNCTIONS) + list(CONSTANTS) + ["x"], key = len, reverse = True)
    tokens, i = [], 0
    while i < len(text):
        ch = text[i]
        if ch.isdigit() or ch == ".":
            j = i
            while j < len(text) and (text[j].isdigit() or text[j] == "."):
                j += 1
            tokens.append(("num", float(text[i:j])))
            i = j
        elif ch in "+-*/^":
            unary = not tokens or tokens[-1][0] in ("op", "lparen")
            if ch == "-" and unary:
                tokens.append(("op", "neg"))
            elif ch == "+" and unary:
                pass
            else:
                tokens.append(("op", ch))
            i += 1
        elif ch == "(":
            tokens.append(("lparen", ch)); i += 1
        elif ch == ")":
            tokens.append(("rparen", ch)); i += 1
        else:
            for name in names:
                if text.startswith(name, i):
                    if name == "x":
                        tokens.append(("var", "x"))
                    elif name in CONSTANTS:
                        tokens.append(("num", CONSTANTS[name]))
                    else:
                        tokens.append(("func", name))
                    i += len(name)
                    break
            else:
                raise ValueError(f"Unknown character: {ch}")
    return tokens
#i ran into a problem, before sorting the list into longest word at the start, longer words that have shorter words in the start like sinh and sin, would often get mismatched.
#i decide to use a sliding window approach as i had used the same concept regarding my prototype for my tokenizer.



# i'm planning to create an implicit multiplication sorter that uses my list - tokens, and arranges them in a way where 5x would be altered to 5 * x
def add_implicit_multiplication(tokens):
    result = []
    for token in tokens:
        if result and result[-1][0] in ("num", "var", "rparen") \
           and token[0] in ("num", "var", "func", "lparen"):
            result.append(("op", "*"))
        result.append(token)
    return result
# a problem i encountered was when result was empty the program would crash, i resolved this issue by adding the statement - if result and ..



#Researched about the shunting yard algorithm, rpn - reverse polish notation. my first few attempts at coding were messy, after a couple attempts on leetcode, i got the general idea
#The algorithm for the shunting yard algorithm was hard to think of, i simplified the modle by drawing each step on a piece of paper and visualising the core concepts
def to_rpn(tokens):
    output, stack = [], []
    for kind, value in tokens:
        if kind in ("num", "var"):
            output.append((kind, value))
        elif kind == "func" or kind == "lparen" or value == "neg":
            stack.append((kind, value))
        elif kind == "op":
            while (stack and stack[-1][0] == "op"
                and (PREC[stack[-1][1]] > PREC[value]
                     or (PREC[stack[-1][1]] == PREC[value] and value !="^"))):
                output.append(stack.pop())
            stack.append((kind, value))
        elif kind == "rparen":
            while stack and stack[-1][0] != "lparen":
                output.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched brackets")
            stack.pop()
            if stack and stack[-1][0] == "func":
                output.append(stack.pop())
    while stack:
        if stack[-1][0] == "lparen":
            raise ValueError("Mismatched brackets")
        output.append(stack.pop())
    return output
#essentially how this program runs is there are two lists: outputs, and stack. all numbers or variables go into the output function. 
#all operators go into our stack list - until an operator's precendence weaker than the previous. while the previous operator is greater than or equal to current, they will continue to be flushed into the output list
#parenthesises are added to the stack, since the kind is not "op" the while loop does not run for values before. when right parenthesis is added, the left parenthesis is removed from the stack list, therefore, giving an order of precedence.

#now i'll code my evaluator
def evaluate(rpn, x):
    stack = []
    try:
        for kind, value in rpn:
            if kind == "num":
                stack.append(value)
            elif kind == "var":
                stack.append(x)
            elif kind == "func":
                stack.append(FUNCTIONS[value](stack.pop()))
            elif value == "neg":
                stack.append(-stack.pop())
            else:
                b = stack.pop()
                a = stack.pop()
                stack.append(OPS[value](a, b))
        return stack[0]
    except IndexError:
        raise SyntaxError("Invalid expression")
    except (ZeroDivisionError, ValueError, OverflowError):
        return float("nan")
#evaluator was a bit difficult to get my head around using the shunting algorithm but i came to the correct conclusion after multiple failed attempts
#every number is added to stack, since x now has a number and is no longer a letter, when "x" the string shows up, x the variable is added - basic concept
#the harder part was using the idea the operator uses the first two values and the concept of last in first out to apply the operator in the correct order




 # tan breaks the graph since matplotlib joins points with straight lines near pi/2 -
 # the first is a huge positive number and thesecond is a huge negative one, matplotlib draws a near verticle line between them

def add_function():
     text = input("y = ")
     try:
         rpn = to_rpn(add_implicit_multiplication(tokenize(text)))
         evaluate(rpn, 1)
     except (ValueError, SyntaxError) as e:
         print("Error:", e)
         return
     functions.append({"text": text, "rpn": rpn})

def set_domain():
    try:
        start, end = map(float, input("Domain of x (start, end): ").split(","))
    except ValueError:
        print("Enter two numbers seperated by a comma")
        return
    if start >= end:
        print("Start must be smaller than end")
        return
    domain[0], domain[1] = start, end 
    
def plot_all():
    if not functions:
        print("Add a function first")
        return
    x_val = np.linspace(domain[0], domain[1], 500).tolist()
    for f in functions:
        y_val = [evaluate(f["rpn"], x) for x in x_val]
        plt.plot(x_val, y_val, label = "y = " + f["text"])
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Graph")
    plt.grid(True)
    plt.legend()
    plt.show()

while True:
    choice = input("""
    1. Add function
    2. Set domain
    3. Plot
    4. Clear all functions
    5. Quit
    """).strip()
    if choice == "1":
        add_function()
    elif choice == "2":
        set_domain()
    elif choice == "3":
        plot_all()
    elif choice == "4":
        functions.clear()
    elif choice == "5":
        break
    else:
        print("Invalid choice")