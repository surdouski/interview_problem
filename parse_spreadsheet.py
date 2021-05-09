"""
Author: <name-removed>
Description: Coding section of interview (<company-name-removed>).
"""
import argparse
import string


class FilePathError(Exception):
    pass


class CircularDependencyError(Exception):
    pass


class InvalidReferenceError(Exception):
    pass


class IncorrectlyFormattedCellError(Exception):
    pass


class ColumnNumberLargerThanAlphabetError(Exception):
    pass


def get_key(row_num, col_num):
    return f'{col_num}{row_num}'


class Sheet:
    @property
    def cell_graph(self):
        return self._cell_graph

    @property
    def dependency_graph(self):
        return self._dependency_graph

    @property
    def sorted_cells(self):
        return self._sorted_cells

    def __init__(self, lines):
        self._input = lines
        self._cell_graph = {}
        self._dependency_graph = {}
        self._sorted_cells = []

    def get_cell(self, cell_key):
        # could use dunder method here to reference as
        #   if it were an array or dict
        try:
            return self.cell_graph[cell_key]
        except IndexError:
            raise InvalidReferenceError

    def build_cell_graph(self):
        for row_num, row in enumerate(self._input, start=1):
            self._parse_row(row_num, row)

    def _parse_row(self, row_num, row):
        alphabet = string.ascii_uppercase  # alphabet used for columns
        row = row.strip('\n').split(',')   # remove line breaks and delimit by comma
        if len(row) > 26:
            raise ColumnNumberLargerThanAlphabetError(
                f'Column numbers exceeding alphabet are '
                f'outside scope of requirements.')
        for col_num, cell_text in enumerate(row):
            cell_key = f'{alphabet[col_num]}{row_num}'
            self._cell_graph[cell_key] = get_parsed_cell(cell_text)

    def build_dependency_graph(self):
        for cell_key, cell in self.cell_graph.items():
            for dependency_key in cell.dependencies:
                self._add_dependency_to_graph(cell_key, dependency_key)

    def _add_dependency_to_graph(self, cell_key, dependency_key):
        if not self._dependency_graph.get(dependency_key):
            self._dependency_graph[dependency_key] = []
        self._dependency_graph[dependency_key].append(cell_key)

    def validate(self):
        self._check_references()
        self._sort()

        if self._circular_dependencies_exist():
            textual_dependencies = ''
            for key in self.dependency_graph:
                textual_dependencies += key + ', '
            raise CircularDependencyError(f'The following cells contain'
                f' cyclic dependencies: {textual_dependencies}')

    def _check_references(self):
        for key in self.dependency_graph:
            if key not in self.cell_graph.keys():
                raise InvalidReferenceError(f'Referenced cell which does not exist.')

    def _sort(self):
        keys_with_no_dependencies = []

        for key, cell in self.cell_graph.items():
            if not cell.dependencies:
                keys_with_no_dependencies.append(key)

        while keys_with_no_dependencies:
            prev_key = keys_with_no_dependencies.pop()
            self._sorted_cells.append(
                {'key': prev_key, 'cell': self.get_cell(prev_key)})

            while self.dependency_graph.get(prev_key):  # while list not empty
                check_key = self.dependency_graph.get(prev_key).pop()
                for dependency_key in self.get_cell(check_key).dependencies:
                    if dependency_key not in self.dependency_graph.values():
                        keys_with_no_dependencies.append(check_key)

            self._empty_list_cleanup(prev_key)

    def _circular_dependencies_exist(self):
        if self.dependency_graph:
            return True

    def _empty_list_cleanup(self, key):
        try:
            if self.dependency_graph[key]:  # if not empty list, a mistake
                return                      # was made

            del self.dependency_graph[key]
        except KeyError:
            pass

    def evaluate(self):
        for cell_map in self.sorted_cells:
            self._cell_graph[cell_map['key']] = cell_map['cell'].evaluate(self)

    def get_plaintext_lines(self):
        very_long_plaintext_string = ""
        for key, value in self.cell_graph.items():
            if key[0] == "A" and very_long_plaintext_string:
                very_long_plaintext_string += '\n'
            very_long_plaintext_string += f'{value.value},'
        return very_long_plaintext_string


class CellExpression:
    @property
    def value(self):
        return 

    @property
    def operator(self):
        return self._operator

    @property
    def operands(self):
        return self._operands

    @property
    def dependencies(self):
        return [
            operand.value for operand in self.operands
            if operand.is_reference
        ]

    def __init__(self, operator, operands):
        self._operator = operator
        self._operands = operands

    def evaluate(self, sheet):
        operand_one_value = self.operands[0].evaluate(sheet).value
        operand_two_value = self.operands[1].evaluate(sheet).value
        if self.operator == "+":
            return CellOperand(
                operand_one_value + operand_two_value)
        elif self.operator == "-":
            return CellOperand(
                operand_one_value - operand_two_value)
        elif self.operator == "*":
            return CellOperand(
                operand_one_value * operand_two_value)
        elif self.operator == "/":
            return CellOperand(
                operand_one_value / operand_two_value)

    def __str__(self):
        return (
            f'operand one: {self.operands[0]}, '
            f'operand two: {self.operands[1]}, '
            f'operator: {self.operator}')


class CellOperand:
    @property
    def value(self):
        return self._value

    @property
    def is_reference(self):
        return self._is_reference

    @property
    def dependencies(self):
        return [self.value] if self.is_reference else []

    def __init__(self, value):
        try:
            self._value = float(value)
            self._is_reference = False
        except ValueError:
            self._value = value
            self._is_reference = True

    def evaluate(self, sheet):
        if not self.is_reference:
            return self

        while self.is_reference:
            referenced_cell = sheet.get_cell(self.value).evaluate(sheet)
            self._value = referenced_cell.value
            self._is_reference = referenced_cell.is_reference
        return self

    def __str__(self):
        return f'value: {self.value}, is reference: {self.is_reference}'


def get_parsed_cell(cell_text):
    cell_text = cell_text.strip()  # remove leading and trailing whitespace
    cell_array = cell_text.split(' ')  # parse by delimiting whitespace

    equates_to_zero = cell_array is None or cell_array[0] == 0
    if equates_to_zero:
        return CellOperand(0)

    is_value = len(cell_array) == 1
    if is_value:
        return CellOperand(cell_array[0])

    is_expression = len(cell_array) == 3
    if is_expression:
        operands = [CellOperand(cell_array[0]), CellOperand(cell_array[1])]
        return CellExpression(cell_array[2], operands)

    raise IncorrectlyFormattedCellError


def main(args=None):
    with open(args.inputfile, "r") as inputfile:
        sheet = Sheet(inputfile.readlines())

    sheet.build_cell_graph()
    sheet.build_dependency_graph()
    sheet.validate()
    sheet.evaluate()
    sheet.get_plaintext_lines()

    with open(args.outputfile, "w") as outputfile:
        outputfile.write(sheet.get_plaintext_lines())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse a basic plaintext'
        'spreadsheet.')
    parser.add_argument('inputfile')
    parser.add_argument('outputfile')
    args = parser.parse_args()

    main(args)
    exit()
