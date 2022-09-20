from lark import Lark, Visitor

kwargs_dict = dict()
args_list = []
command_str = ''
commands_list = []

line_grammar = r"""
  ?start: commands
    
    !commands   : command (args* kwargs*)*  
    !command    : word
    kwargs      : kwarg*
    args        : arg*
    arg        : val
    kwarg      : kw "=" val*
    
    !kw         : string_simple
    !val        : string_simple | string_quoted
    ?string_quoted  : /[\"].*[\"]|[\'].*[\']/
    ?word           : WORD
    ?string_simple  : /[^\s,^=]+/
    ?number         : SIGNED_NUMBER
    
    %import common.WORD
    %import common.SIGNED_NUMBER
    %import common.WS
    
    %ignore WS
    %ignore /,/
  """

class ConvertElementsOfDict(Visitor):
    # converts kwargs to dictionary
    def kwarg(self, tree):
        assert tree.data == "kwarg"
        val_list = []

        # tree.children[i].data -> kw, val1, val2, ...
        kw = ''+tree.children[0].children[0].value  # value of kw (str)

        i = 1
        while (1):  # making list of vals in kw
            try:
                val_list.append(''+tree.children[i].children[0].value)
            except:
                break
            i = i + 1

        global kwargs_dict
        kwargs_dict[kw] = val_list

    # converts args to list
    def arg(self, tree):
        assert tree.data == "arg"
        global args_list
        args_list.append('' + tree.children[0].children[0].value)

    def command(self, tree):
        assert tree.data == "command"
        global command_str
        command_str = tree.children[0].value

def convertToDict(dictionary):
    dictionary["command"] = command_str
    dictionary["args"] = args_list
    dictionary["kwargs"] = kwargs_dict
    return dictionary

def readFileAndConvert(file_name):
    temp_dict = {
        "command": "",
        "args": "",
        "kwargs": ""
    }
    dictionary = dict()

    line_parser = Lark(line_grammar)
    parse = line_parser.parse

    file = open(file_name, "r")
    line = file.readline()

    while line:
        tree = parse(line)
        ConvertElementsOfDict().visit(tree)
        temp_dict = convertToDict(temp_dict)
        commands_list.append(temp_dict)
        line = file.readline()
    file.close()

    dictionary["commands"] = commands_list
    return dictionary

# writes dictionary to file
def writeDictToFile(file_name, dictionary):
    file = open(file_name, "w")
    file.write(str(dictionary))
    file.close()


if __name__ == '__main__':
    dictionary = readFileAndConvert("file.txt")
    writeDictToFile("dictionary.txt", dictionary)
