import argparse

parser = argparse.ArgumentParser(prog='mogami')
required = parser.add_argument_group('required arguments')
required.add_argument('-d', '--dialy', action='store_true')
required.add_argument('-s', '--sortie', metavar='sortie_map')
required.add_argument('-m', '--manual', metavar='kill_required', type=int)
args = parser.parse_args()
