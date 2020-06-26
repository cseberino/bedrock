#!/usr/bin/env python3
#
# Copyright 2020 Christian Seberino
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest
import subprocess
import warnings

SUM     = "[[PLUS, [[PLUS, [[PLUS, %d], %d]], %d]], %d]"
DIFF    = "[[MINUS, [[MINUS, [[MINUS, %d], %d]], %d]], %d]"
ABBREVS = {"PLUS"    : "[λ, x, [λ, y, [λ, z, [λ, t, [[x, z], [[y, z], t]]]]]]",
           "MINUS"   : "[λ, x, [λ, y, [[y, [λ, x, [λ, z, [λ, t, [[[x, [λ, u" + \
                          ", [λ, v, [v, [u, z]]]]], [λ, w, t]], [λ, w, w]]]" + \
                          "]]], x]]]",
           "MULT"    : "[λ, x, [λ, y, [λ, z, [y, [x, z]]]]]",
           "EXP"     : "[λ, x, [λ, y, [y, x]]]",
           "SUCC"    : "[λ, x, [λ, y, [λ, z, [y, [[x, y], z]]]]]",
           "PRED"    : "[λ, x, [λ, y, [λ, z, [[[x, [λ, t, [λ, u, [u, [t, y]" + \
                          "]]]], [λ, v, z]], [λ, v, v]]]]]",
           "TRUE"    : "[λ, x, [λ, y, x]]",
           "FALSE"   : "[λ, x, [λ, y, y]]",
           "AND"     : "[λ, x, [λ, y, [[x, y], x]]]",
           "OR"      : "[λ, x, [λ, y, [[x, x], y]]]",
           "NOT"     : "[λ, x, [λ, y, [λ, z, [[x, z], y]]]]",
           "IF"      : "[λ, x, [λ, y, [λ, z, [[x, y], z]]]]",
           "IS_ZERO" : "[λ, x, [[x, [λ, y, [λ, x, [λ, y, y]]]], [λ, x, [λ, " + \
                          "y, x]]]]"}

def num_func(n, x = "x", y = "y"):
        return "[λ, " + x + ", [λ, " + y  + ", " + n * ("[" + x + ", ") + y +  \
                                                               ((n + 2) * "]")

class Tester(unittest.TestCase):
        def setUp(self):
                warnings.simplefilter("ignore", ResourceWarning)

        def do_num_test(self, e, num):
                for f in ABBREVS:
                        e = e.replace(f, ABBREVS[f])
                for i in range(10):
                        e = e.replace(str(i), num_func(i))
                command = 'echo "%s" | ../bedrock' % e
                output  = subprocess.check_output(command, shell = True)
                output  = output.strip().decode()
                atom_1  = sorted(list(set(output)))[-2]
                atom_2  = sorted(list(set(output)))[-3]
                answers = [num_func(num, atom_1, atom_2),
                           num_func(num, atom_2, atom_1)]
                self.assertIn(output, answers)

        def do_test(self, e, answer):
                for f in ABBREVS:
                        e = e.replace(f, ABBREVS[f])
                for i in range(10):
                        e = e.replace(str(i), num_func(i))
                command = 'echo "%s" | ../bedrock' % e
                output  = subprocess.check_output(command, shell = True)
                output  = output.strip().decode()
                atoms_o = sorted(list(set(output)))
                if len(atoms_o) > 1:
                        xx       = sorted(list(set(answer)))[-2]
                        yy       = sorted(list(set(answer)))[-3]
                        answer   = answer.replace(xx, "A")
                        answer   = answer.replace(yy, "B")
                        answer_1 = answer.replace("A", atoms_o[-2])
                        answer_1 = answer_1.replace("B", atoms_o[-3])
                        answer_2 = answer.replace("B", atoms_o[-2])
                        answer_2 = answer_2.replace("A", atoms_o[-3])
                        self.assertIn(output, [answer_1, answer_2])
                else:
                        self.assertEqual(output, answer)

        def test_all(self):
                self.do_test("a",                         "a")
                self.do_test("b",                         "b")
                self.do_test("x",                         "x")
                self.do_test("y",                         "y")
                self.do_test("[λ, a, b]",                 "[λ, a, b]")
                self.do_test("[λ, x, y]",                 "[λ, x, y]")
                self.do_test("[λ, a, [b, c]]",            "[λ, a, [b, c]]")
                self.do_test("[λ, a, [λ, b, c]]",         "[λ, a, [λ, b, c]]")
                self.do_test("[a, b]",                    "[a, b]")
                self.do_test("[x, y]",                    "[x, y]")
                self.do_test("[a, [b, [c, d]]]",          "[a, [b, [c, d]]]")
                self.do_test("[[λ, a, a], b]",            "b")
                self.do_test("[[λ, x, [x, x]], y]",       "[y, y]")
                self.do_test("[[λ, a, [a, b]], [x, y]]",  "[[x, y], b]")
                self.do_test("[[λ, a, [a, a]], [x, y]]",  "[[x, y], [x, y]]")
                self.do_test("[[λ, a, [λ, b, a]], c]",    "[λ, b, c]")
                self.do_test("[λ, a, [λ, b, [c, d]]]",
                             "[λ, a, [λ, b, [c, d]]]")
                self.do_test("[λ, a, [λ, b, [λ, c, d]]]",
                             "[λ, a, [λ, b, [λ, c, d]]]")
                for i in range(10):
                        for j in range(10):
                                self.do_num_test("[[PLUS, %d], %d]" % (i, j),
                                                 i + j)
                for i in range(5):
                        for j in range(5):
                                for k in range(5):
                                        for l in range(5):
                                                sum_ = i + j + k + l
                                                e    = SUM % (i, j, k, l)
                                                self.do_num_test(e, sum_)
                for i in range(10):
                        for j in range(min(i + 1, 4)):
                                self.do_num_test("[[MINUS, %d], %d]" % (i, j),
                                                     i - j)
                for i in range(5):
                        for j in range(5):
                                for k in range(5):
                                        for l in range(5):
                                                num = i - j - k - l
                                                if num >= 0:
                                                        e = DIFF % (i, j, k, l)
                                                        self.do_num_test(e, num)
                for i in range(5):
                        for j in range(5):
                                self.do_num_test("[[MULT, %d], %d]" % (i, j),
                                                 i * j)
                for i in range(1, 3):
                        for j in range(1, 3):
                                program = "[[EXP, %d], %d]" % (i, j)
                                self.do_num_test(program, i ** j)
                for i in range(10):
                        self.do_num_test("[SUCC, [SUCC, [SUCC, %d]]]" % i,
                                         i + 3)
                for i in range(3, 10):
                        self.do_num_test("[PRED, [PRED, [PRED, %d]]]" % i,
                                         i - 3)
                self.do_test("[[AND, TRUE], TRUE]",   "[λ, x, [λ, y, x]]")
                self.do_test("[[AND, TRUE], FALSE]",  "[λ, x, [λ, y, y]]")
                self.do_test("[[AND, FALSE], TRUE]",  "[λ, a, [λ, b, b]]")
                self.do_test("[[AND, FALSE], FALSE]", "[λ, a, [λ, b, b]]")
                self.do_test("[[OR, TRUE], TRUE]",    "[λ, a, [λ, b, a]]")
                self.do_test("[[OR, TRUE], FALSE]",   "[λ, b, [λ, a, b]]")
                self.do_test("[[OR, FALSE], TRUE]",   "[λ, x, [λ, y, x]]")
                self.do_test("[[OR, FALSE], FALSE]",  "[λ, x, [λ, y, y]]")
                self.do_test("[NOT, TRUE]",           "[λ, a, [λ, z, z]]")
                self.do_test("[NOT, FALSE]",          "[λ, a, [λ, z, a]]")
                self.do_test("[[[IF, TRUE], 5], 8]",  num_func(5, "b", "a"))
                self.do_test("[[[IF, FALSE], 5], 8]", num_func(8, "x", "y"))
                self.do_test("[IS_ZERO, 8]",          "[λ, d, [λ, c, c]]")
                self.do_test("[IS_ZERO, 0]",          "[λ, b, [λ, a, b]]")

unittest.main()
