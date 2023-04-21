import math
import numpy as np
import tabula
import PyPDF2
import re
import izu_proj1_generator as gen
import copy
import argparse
import glob


def print_grid(grid, indent=0):
    for i in range(grid.shape[0]):
        print("\t" * indent, end="")
        for j in range(grid.shape[1]):
            if grid[i][j] == -1:
                print("Z", end=" ")
            else:
                print(grid[i][j], end=" ")
        print()


parser = argparse.ArgumentParser(description="IZU IZU izi ;)")
parser.add_argument(
    "-p",
    "--pdf_path",
    type=str,
    help="path to the pdf you received by mail",
    default=None,
)
parser.add_argument(
    "-l",
    "--latex",
    help="generate LaTeX output tp xlogin.tex",
    action="store_true",
)
parser.add_argument(
    "-n",
    "--name",
    type=str,
    help="specify if exporting to LaTeX and your name has diacritics/accents",
    default=None,
)
parser.add_argument("--verbose", help="verbose mode", action="store_true")
parser.add_argument("-s", "--silent", help="silent mode", action="store_true")

args = parser.parse_args()

if args.pdf_path is None:
    files = glob.glob("./x*.pdf")
    if len(files) == 0:
        print("No pdf found in current directory")
        print("Please specify path to pdf file")
        exit(1)
    elif len(files) > 1:
        print("More than one pdf found in current directory")
        print("Please specify path to pdf file")
        exit(1)
    pdf_path = files[0]
else:
    pdf_path = args.pdf_path
tables = tabula.read_pdf(pdf_path, pages=1, encoding="utf-8")
tables[0] = tables[0].drop(tables[0].columns[0], axis=1)
grid = tables[0].to_numpy()
grid_copy_for_export = copy.deepcopy(grid)
grid[grid == "Z"] = -1
grid = grid.astype(int)

reader = PyPDF2.PdfReader(pdf_path)
pdf_text = reader.pages[0].extract_text()

start_regex = r"Start: \(\[(\d{1}), (\d{1})], (\d\.\d), \[null]\)"

start_match = re.search(start_regex, pdf_text)
if not args.silent:
    print("Parsed data from pdf (check for errors):")
    print("\t", start_match.groups())
end_regex = r"C´ ıl: \(\[(\d{1}), (\d{1})\], X, \[\?, \?\]\)"
end_match = re.search(end_regex, pdf_text)
if not args.silent:
    print("\t", end_match.groups())
name_and_login_regex = r"Jm´ eno:\ *(.*)\nLogin: (x.*)\n"
name_and_login_match = re.search(name_and_login_regex, pdf_text)
if not args.silent:
    print("\t", name_and_login_match.groups())
assert len(start_match.groups()) == 3
assert len(end_match.groups()) == 2
assert len(name_and_login_match.groups()) == 2

if not args.silent:
    print_grid(grid, 1)
grid_cost = grid

grid_f = np.zeros(shape=(10, 10))
grid_f.fill(-1)
grid_g = np.zeros(shape=(10, 10))


class Point:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent
        self.g_for_export = 0
        self.h_for_export = 0
        self.f_for_export = 0

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y, self.parent))

    def __repr__(self):
        if self.parent is None:
            return "([{}, {}], {}, [null])".format(
                self.x, self.y, round(self.f_for_export, 2)
            )
        return "([{}, {}], {}, [{}, {}])".format(
            self.x,
            self.y,
            round(self.f_for_export, 2),
            self.parent.x,
            self.parent.y,
        )


start_point = Point(
    int(start_match.group(1)),
    int(start_match.group(2)),
)
end_point = Point(int(end_match.group(1)), int(end_match.group(2)))
start_point.f_for_export = float(start_match.group(3))

CLOSED = []
OPEN = [start_point]
WORK_ORDER = [start_point]


def distance(first_point, second_point):
    return round(
        math.sqrt(
            (first_point.x - second_point.x) ** 2
            + (first_point.y - second_point.y) ** 2
        ),
        2,
    )


def moore_neighbours(point):
    neighbours = []
    for j in range(
            -1,
            2,
        ):
        for i in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if point.x + i < 0 or point.x + i > 9 or point.y + j < 0 or point.y + j > 9:
                continue
            if grid_cost[point.y + j][point.x + i] == -1:
                continue
            neighbours.append(Point(point.x + i, point.y + j, point))
            if Point(point.x + i, point.y + j, point) not in WORK_ORDER:
                WORK_ORDER.append(Point(point.x + i, point.y + j, point))
    return neighbours


def calculate_step(current):
    for neighbour in moore_neighbours(current):
        if current == start_point:
            current.f_for_export = float(start_match.group(3))
        if neighbour in CLOSED:
            continue
        if neighbour not in OPEN:
            OPEN.append(neighbour)
        if (
            grid_g[current.y][current.x] + grid_cost[neighbour.y][neighbour.x]
            < grid_g[neighbour.y][neighbour.x]
            or grid_g[neighbour.y][neighbour.x] == 0
        ):
            grid_g[neighbour.y][neighbour.x] = (
                grid_g[current.y][current.x] + grid_cost[neighbour.y][neighbour.x]
            )
            grid_f[neighbour.y][neighbour.x] = grid_g[neighbour.y][
                neighbour.x
            ] + distance(neighbour, end_point)
            neighbour.f_for_export = grid_f[neighbour.y][neighbour.x]


step = 0
iterations = []


def update_points_for_export():
    for point in OPEN:
        point.g_for_export = round(grid_g[point.y][point.x], 2)
        point.h_for_export = round(distance(point, end_point), 2)
        point.f_for_export = round(grid_f[point.y][point.x], 2)
    for point in CLOSED:
        point.g_for_export = round(grid_g[point.y][point.x], 2)
        point.h_for_export = round(distance(point, end_point), 2)
        point.f_for_export = round(grid_f[point.y][point.x], 2)
    for point in WORK_ORDER:
        point.g_for_export = round(grid_g[point.y][point.x], 2)
        point.h_for_export = round(distance(point, end_point), 2)
        point.f_for_export = round(grid_f[point.y][point.x], 2)

while OPEN:
    step += 1
    if not args.silent:
        print("Step {}".format(step))
        print("OPEN: {}".format(OPEN))
        print("CLOSED: {}".format(CLOSED))
        if args.verbose:
            print("Grid G:\n{}".format(grid_g))
            print("Grid F:\n{}".format(grid_f))
    current = OPEN[0]

    iterations.append([copy.deepcopy(OPEN), copy.deepcopy(CLOSED)])

    for point in OPEN:
        if grid_f[point.y][point.x] < grid_f[current.y][current.x]:
            current = point
        elif grid_f[point.y][point.x] == grid_f[current.y][current.x]:
            if distance(point, end_point) < distance(current, end_point):
                current = point
    OPEN.remove(current)
    CLOSED.append(current)
    calculate_step(current)
    if end_point in OPEN:
        step += 1
        iterations.append([copy.deepcopy(OPEN), copy.deepcopy(CLOSED)])
        update_points_for_export()
        end_point.parent = current
        current = end_point
        break
if not args.silent:
    print("Step {}".format(step))
    print("OPEN: {}".format(OPEN))
    print("CLOSED: {}".format(CLOSED))
    if args.verbose:
        print("Grid G:\n{}".format(grid_g))
        print("Grid F:\n{}".format(grid_f))
    print("\n\nPath found in {} steps".format(step))
path = []

while current.parent is not None:
    path.append(current)
    current = current.parent
current.f_for_export = float(start_match.group(3))
path.append(current)
path.reverse()
if not args.silent:
    print("Path: {}".format(path))
if args.name is not None:
    gen.name = args.name
else:
    gen.name = name_and_login_match.group(1)
gen.login = name_and_login_match.group(2)

gen.start = (int(start_match.group(1)), int(start_match.group(2)))

gen.end = (int(end_match.group(1)), int(end_match.group(2)))

gen.initial_cost = float(start_match.group(3))

gen.mapa = [list(map(str, i)) for i in grid_copy_for_export.tolist()]

gen.iterace = iterations

gen.vysledna_cesta = list(map(lambda x: (x.x, x.y), path))

listtt = list(
    map(
        lambda x: ((x.x, x.y), x.g_for_export, x.h_for_export, x.f_for_export),
        WORK_ORDER,
    )
)

gen.pomocna_tabulka = listtt

if args.latex:
    output_file = open("{}.tex".format(gen.login), "w")
    output_file.write(gen.get_latex())
