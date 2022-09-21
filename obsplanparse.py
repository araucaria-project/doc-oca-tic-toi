import copy

from lark import Lark, Visitor


line_grammar = r"""
  ?start: commands

!commands   : command (args* kwargs*)* 
!command    : word 
kwargs      : kwarg* 
args        : arg* 
arg         : val 
kwarg       : kw "=" val* 

!kw             : string_simple
!val            : string_simple | string_quoted
?string_quoted  : /[\"].*[\"]|[\'].*[\']/
?word           : WORD
?string_simple  : /[^\s,^=]+/
?number         : SIGNED_NUMBER

%import common.WORD
%import common.SIGNED_NUMBER
%import common.WS

%ignore WS
%ignore /,/
%ignore /#.*/
  """


class ConvertElementsOfDict(Visitor):

    def __init__(self) -> None:
        super().__init__()
        self.kwargs_dict = {}
        self.args_list = []
        self.command_str = ''

    def kwarg(self, tree):
        """converts kwargs to dictionary"""
        assert tree.data == "kwarg"
        val_list = []

        # tree.children[i].data -> kw, val1, val2, ...
        kw = ''+tree.children[0].children[0].value  # value of kw (str)

        # for child  in tree.children:
        #     val_list.append('' + child.children[0].value)

        i = 1
        while True:  # make list of vals in kw
            try:
                val_list.append(''+tree.children[i].children[0].value)
            except:
                break
            i = i + 1

        self.kwargs_dict[kw] = val_list

    # converts args to list
    def arg(self, tree):
        assert tree.data == "arg"
        self.args_list.append('' + tree.children[0].children[0].value)

    def command(self, tree):
        assert tree.data == "command"
        self.command_str = tree.children[0].value


# converts one command (line)
def convertToDict(visitor):
    ret_dict = {
        "command": visitor.command_str,
        "args": visitor.args_list,
        "kwargs": visitor.kwargs_dict
    }
    return ret_dict


def readFileAndConvert(file_name):
    dictionary = dict()
    commands_list = []

    line_parser = Lark(line_grammar)
    parse = line_parser.parse

    with open(file_name, "r") as file:
        for line in file:

            tree = parse(line)
            visitor = ConvertElementsOfDict()
            visitor.visit(tree)

            command_dict = convertToDict(visitor)

            commands_list.append(command_dict)



    dictionary["commands"] = commands_list
    return dictionary


# writes dictionary to file
def writeDictToFile(file_name, dictionary):
    file = open(file_name, "w")
    file.write(str(dictionary))
    file.close()


if __name__ == '__main__':
    dictionary = readFileAndConvert("tests/file3.txt")
    writeDictToFile("dictionary.txt", dictionary)
