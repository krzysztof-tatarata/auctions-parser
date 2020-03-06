import argparse
from app.auctions import Auctions

parser = argparse.ArgumentParser()
parser.add_argument('-pages', action='store', dest='pages', help='Set pagination pages to parse, comma separated values')
parser.add_argument('-pages_range', action='store', dest='pages_range', help='Set pagination pages range to parse, comma separated range values')
args = parser.parse_args()

pages = set()
if args.pages_range:
    pages = set(range(int(args.pages_range.split(',')[0]), int(args.pages_range.split(',')[1])+1))
if args.pages:
    pages = pages.union(map(int, args.pages.split(',')))
if not(args.pages_range and args.pages):
    pages = {1}

obj = Auctions()
for page in pages:
    auctions = obj.get_auctions(page)
    obj.set_auctions(auctions)