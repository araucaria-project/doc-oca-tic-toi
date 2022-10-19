from lark import Lark
from lark.visitors import Interpreter

line_grammar = r"""
?start: sequences

!sequences      : sequence*
!sequence       : end_line* begin_sequence args kwargs comment? separator all_commands end_sequence comment? (end_line* comment?)*
!all_commands   : (command separator)*
!command        : (command_name args kwargs | sequence) comment?
!command_name   : word
kwargs          : kwarg*
args            : val*
kwarg           : kw "=" (val ",")+ val | kw "=" val

!begin_sequence : "BEGINSEQUENCE"
!end_sequence   : "ENDSEQUENCE"
separator       : end_line+
word            : /[^{BEGINSEQUENCE}{ }][A-Z]+/
comment         : /#.*/
end_line        : /\n/
!kw             : string_simple
!val            : string_simple | string_quoted
?string_quoted  : /[\"].*[\"]|[\'].*[\']/
?string_simple  : /[^\s=\'\"]+/

%ignore /[ \f]+/
  """


class ConvertElemsOfSeq(Interpreter):
    def __init__(self) -> None:
        super().__init__()
        self.kwargs_dict = {}
        self.args_list = []
        self.command_str = ''
        self.command_dict = {}
        self.all_commands_list = []
        self.sequence_dict = {}
        self.in_sequence = True

    def sequences(self, tree):
        assert tree.data == "sequences"
        self.sequence_dict = []
        self.in_sequence = True

    def sequence(self, tree):
        assert tree.data == "sequence"
        self.in_sequence = True

    def command(self, tree):
        """ clears command str, and command dict """
        assert tree.data == "command"
        self.command_dict = {}
        self.command_str = ''
        self.in_sequence = False

    def command_name(self, tree):
        assert tree.data == "command_name"
        self.command_str = tree.children[0].children[0].value

    def args(self, tree):
        """ asserts vals of arg to args list """
        assert tree.data == "args"
        val_list = []
        i = 0

        while True:  # make list of vals in kw
            try:
                val_list.append('' + tree.children[i].children[0].value)
            except:
                break
            i = i + 1

        self.args_list = val_list

    def kwarg(self, tree):
        """ asserts kw and vals of kwarg to kwargs dict """
        assert tree.data == "kwarg"
        val_list = []

        # tree.children[i].data -> kw, val1, val2, ...
        kw = '' + tree.children[0].children[0].value  # value of kw (str)

        # for child  in tree.children:
        #     val_list.append('' + child.children[0].value)

        i = 1
        while True:  # make list of vals in kw
            try:
                val_list.append(tree.children[i].children[0].value)
            except:
                break
            i = i + 1

        self.kwargs_dict[kw] = val_list


def buildSequences(tree, visitor):
    iterator = iter(tree.children)
    sequences_list = []

    for child in iterator:
        visitor.visit(child)

        if child.data == "sequence":
            temp_visitor = buildSequence(child, visitor, {}, [])
            sequences_list.append(temp_visitor.sequence_dict.copy())

    return sequences_list


def buildSequence(tree, visitor, seq_kwargs_dict, seq_args_list):
    iterator = iter(tree.children)

    for child in iterator:
        visitor.visit(child)

        if child.data == "begin_sequence":
            visitor.sequence_dict["begin_sequence"] = "begin"

        if child.data == "args":
            try:
                if child.children[0].children[0].data == "val":
                    buildArgsOrKwargs(child, visitor)
            except:
                None

            visitor.sequence_dict["args"] = visitor.args_list
            seq_args_list = visitor.args_list
            visitor.args_list = []
            child = next(iterator)

        if child.data == "kwargs":
            try:
                if child.children[0].children[0].data == "val":
                    buildArgsOrKwargs(child, visitor)
            except:
                None

            visitor.sequence_dict["kwargs"] = visitor.kwargs_dict.copy()
            seq_kwargs_dict = visitor.kwargs_dict.copy()
            visitor.kwargs_dict = {}
            child = next(iterator)

        if child.data == "all_commands":
            visitor.sequence_dict["all_commands"] = buildAllCommands(child, visitor).copy()
            break

        try:
            buildSequence(child, visitor, seq_kwargs_dict, seq_args_list)
        except:
            None

    if seq_args_list:
        visitor.sequence_dict["args"] = seq_args_list.copy()

    if seq_kwargs_dict != {}:
        visitor.sequence_dict["kwargs"] = seq_kwargs_dict.copy()

    return visitor


def buildAllCommands(tree, visitor):
    temp_all_commands_list = []
    iterator = iter(tree.children)

    for child in iterator:
        visitor.visit(child)

        if child.data == "command":
            if child.children[0].data == "command_name":
                buildCommand(child, visitor)
                temp_all_commands_list.append(visitor.command_dict.copy())

            if child.children[0].data == "sequence":
                visitor.sequence_dict["args"] = []
                visitor.sequence_dict["kwargs"] = {}
                buildSequence(child, visitor, {}, [])
                temp_all_commands_list.append(visitor.sequence_dict.copy())

    return temp_all_commands_list


def buildCommand(tree, visitor):
    for child in tree.children:
        visitor.visit(child)
        try:
            visitor = buildCommand(child, visitor)
        except:
            None

        if child.data == "command_name":
            visitor.command_dict["command_name"] = visitor.command_str

        if child.data == "args":
            buildArgsOrKwargs(child, visitor)
            visitor.command_dict["args"] = visitor.args_list
            visitor.args_list = []

        if child.data == "kwargs":
            buildArgsOrKwargs(child, visitor)
            visitor.command_dict["kwargs"] = visitor.kwargs_dict
            visitor.kwargs_dict = {}

    return visitor


def buildArgsOrKwargs(tree, visitor):
    for child in tree.children:
        visitor.visit(child)
        try:
            visitor = buildArgsOrKwargs(child, visitor)
        except:
            None

    return visitor


def readFileAndConvert(file_name):
    """ reads file and converts code to dictionary """
    line_parser = Lark(line_grammar)
    parse = line_parser.parse

    with open(file_name, "r") as file:
        text = str(file.read())
        tree = parse(text)
        visitor = ConvertElemsOfSeq()
        sequences = buildSequences(tree, visitor)
        return sequences


def writeDictToFile(file_name, dictionary):
    """ writes dictionary to file """
    file = open(file_name, "w")
    file.write(str(dictionary))
    file.close()


if __name__ == '__main__':
    dictionary = readFileAndConvert("tests/file3.txt")
    writeDictToFile("dictionary.txt", dictionary)
