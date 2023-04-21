import numpy
import argparse
import glob
import sys

fix_text = """a vysledek zapiste na radcich c. 26, 27, 28 a 29 ve formatu stejnem jako
vyse, tj. ve tvaru matice s cisly zaokrouhlenymi na tri desetinna mista.
Oznaceni stavu s odmenami ponechejte v puvodnich tvarech!

Reseni: 
"""
custom = False

parser = argparse.ArgumentParser(description="IZU IZU izi ;)")
parser.add_argument(
    "-f",
    "--file",
    type=str,
    help="path to the ORIGINAL txt you received by mail, do not fix it your self",
    default=None,
)
parser.add_argument(
    "-a",
    "--alpha",
    type=float,
    help="specify a custom alpha value",
    default=None,
)
parser.add_argument(
    "-b",
    "--beta",
    type=float,
    help="specify a custom beta value",
    default=None,
)
parser.add_argument(
    "-c",
    "--cfile",
    type=str,
    help="specify a custom file, table must be in the same style as in the mail",
    default=None,
)

parser.add_argument("--verbose", help="verbose mode", action="store_true")
parser.add_argument("-s", "--silent", help="silent mode", action="store_true")

args = parser.parse_args()

if args.file is None:
    files = glob.glob("./x*.txt")
    if len(files) == 0:
        print("No xlogin.txt found in current directory")
        print("Please specify path to file")
        exit(1)
    elif len(files) > 1:
        print("More than one xlogin.txt found in current directory")
        print("Please specify path to file")
        exit(1)
    filename = files[0]
else:
    filename = args.file

if args.cfile is not None:
    if args.file is not None:
        print(
            "WARNING: You specified a file and also a custom file, continuing with custom file as default"
        )
    filename = args.cfile
    custom = True


def print_formated_table(table, rewards):
    output_table = numpy.array(
        list(
            map(
                lambda x, xr: list(
                    map(
                        lambda y, yr: format(y.round(3), ".3f")
                        if yr == 0
                        else "rew=" + str(int(yr)),
                        x,
                        xr,
                    )
                ),
                table,
                rewards,
            )
        )
    )
    for line in output_table:
        for num in line:
            print(" " * (6 - len(num)), num, end="")
        print()


class TD:
    def __init__(self, filename, alpha, beta, custom) -> None:
        self.filepath = filename
        self.paths = []

        self.read_file_contents(self.filepath, alpha, beta, custom)
        self.solve()
        self.generate_output()
        pass

    def read_file_contents(self, filename, alpha, beta, custom):
        self.file_contets = open(filename, "r").readlines()

        if not custom:
            table_text = self.file_contets[12:16]

        else:
            x, y = list(map(lambda x: int(x.strip()), self.file_contets[0].split("x")))
            table_text = self.file_contets[1 : y + 1]

        table_arr = list(map(lambda x: x.strip().split(), table_text))

        self.rewards = numpy.array(
            list(
                map(
                    lambda x: list(
                        map(
                            lambda y: float(y.split("=")[1])
                            if (y == "rew=1" or y == "rew=-1")
                            else float(0),
                            x,
                        )
                    ),
                    table_arr,
                )
            )
        )

        table_arr = list(
            map(
                lambda x: list(
                    map(lambda y: float(0) if (y == "rew=1" or y == "rew=-1") else y, x)
                ),
                table_arr,
            )
        )

        table_arr = list(map(lambda x: list(map(lambda y: float(y), x)), table_arr))

        self.table = numpy.array(table_arr)

        if not custom:
            self.paths.append(
                list(map(lambda x: int(x), self.file_contets[18][43:].split()))
            )

        else:
            for i in range(y + 1, len(self.file_contets)):
                self.paths.append(
                    list(map(lambda x: int(x), self.file_contets[i].split()))
                )

        self.alpha = float(self.file_contets[17][40:44]) if alpha is None else alpha

        self.beta = float(self.file_contets[17][52:56]) if beta is None else beta

        print("Alpha set as: {}".format(self.alpha))
        print("Beta set as: {}".format(self.beta))
        print("Path/s to be computed: {}".format(self.paths))
        print("Input table:")
        print_formated_table(self.table, self.rewards)

    def solve_step(self, step, next_step):
        self.table[self.ctti(step)] = self.table[self.ctti(step)] + self.alpha * (
            self.rewards[self.ctti(next_step)]
            + self.beta * (self.table[self.ctti(next_step)] if next_step != 0 else 0)
            - (self.table[self.ctti(step)])
        )

    # Continuous to Table index
    def ctti(self, index):
        return [(index - 1) // self.table.shape[1]], [(index - 1) % self.table.shape[1]]

    def solve(self):
        for index, path in enumerate(self.paths, start=1):
            for i in range(len(path) - 1):
                step = path[i]
                next_step = path[i + 1]
                self.solve_step(step, next_step)
            self.table = numpy.array(
                list(map(lambda x: list(map(lambda y: y.round(3), x)), self.table))
            )
            if args.verbose:
                print("Step: {}".format(index))
                print("_" * self.table.shape[0] * 9)
                print_formated_table(self.table, self.rewards)
                print()

    def generate_output(self):
        output = self.file_contets[:19]
        output = list(map(lambda x: x.replace("\n", ""), output))
        output.append(fix_text)
        if not custom:
            with open("{}_out.txt".format(self.filepath), "w+") as f:
                original_std = sys.stdout
                sys.stdout = f
                for line in output:
                    print(line)
                print_formated_table(self.table, self.rewards)
                sys.stdout = original_std
        print("Result: ")
        print_formated_table(self.table, self.rewards)


if __name__ == "__main__":
    td = TD(filename, args.alpha, args.beta, custom)
