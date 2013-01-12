#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys


def main():
	if len(sys.argv) != 2:
		sys.exit("evaluator.py <filename>")
	else:
		filename = sys.argv[1]
	
		try:
			f = open(filename, "r")
		except IOError:
			sys.exit("Bad file")

		score = process_answers(f)
		f.close()

		print_results(score)


def process_answers(f):
	score = {
		"mrr": 0,
		"mrr2": 0,
		"right": 0,
		"right2": 0,
		"nil": 0,
		"right_nil": 0
	}

	for line in f:
		m = re.match(r"(?P<id>[^ \t]+)[ \t]+(?P<runtag>[^ \t]+)[ \t]+(?P<position>[1-3])[ \t]+(?P<score>[0-9]+)[ \t]+((?P<url>[^ \t]+)[ \t]+)?(?P<answer>[^ \t]+( [^ \t]+)*)[ \t]+\((?P<type>[^ \t]*)\)\n", line)
		
		if m is None:
			print "error:", line,
			continue

		position = int(m.group("position"))
		answer = m.group("answer")
		t = m.group("type")

		if t == "R":
			num = 1.0 / position
			score["mrr"] += num
			score["mrr2"] += num
			score["right"] += 1
			score["right2"] += 1
		elif t == "U":
			score["mrr2"] += 1.0 / position
			score["right2"] += 1

		if answer == "NIL" and position == 1:
			score["nil"] += 1
			if t == "R":
				score["right_nil"] += 1

	return score


def print_results(score):
	print "MRR (strict):\t\t{:>10.3f}".format(score["mrr"])
	print "MRR (permissive)\t{:>10.3f}".format(score["mrr2"])
	print "Right answers (strict):\t{:>6}".format(score["right"])
	print "Right answers (strict):\t{:>6}".format(score["right2"])
	print "NIL answers:\t\t{:>6}".format(score["nil"])
	print "NIL right answers:\t{:>6}".format(score["right_nil"])


if __name__ == '__main__':
	main()
