from rtree import index
import csv

def readtsv(fname):
  with open(fname,'r') as f:
    reader = csv.reader(f,delimiter="\t")
    for row in reader:
      yield row

admin1codes = {}
for row in readtsv('admin1CodesASCII.txt'):
  # concat code -> unicode name
  admin1codes[row[0]] = row[1]

idx = index.Rtree('reverse_geocode')
for row in readtsv('cities1000.txt'):
  gnclass = row[7]
  if gnclass != "PPLX":
    lat = float(row[4])
    lon = float(row[5])
    geonames_id = int(row[0])
    country = row[8]
    admin_1_code = row[10]
    name = row[1]
    concat = country + '.' + admin_1_code
    admin_1 = ''
    if concat in admin1codes:
      admin_1 = admin1codes[concat]
    idx.insert(int(row[0]),(lon,lat,lon,lat),obj=[name,admin_1,country])



