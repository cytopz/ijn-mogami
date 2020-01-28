import argparse

parser = argparse.ArgumentParser(prog='mogami')
required = parser.add_argument_group('required arguments')
required.add_argument('-d', '--dialy', action='store_true')
required.add_argument('-s', '--sortie', metavar='SORTIE_MAP')
args = parser.parse_args()
