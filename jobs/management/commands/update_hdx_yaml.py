from django.core.management.base import BaseCommand
from jobs.models import HDXExportRegion

NEW_YAML = """
Buildings:
  hdx:
    tags: buildings, geodata
    caveats: OpenStreetMap data is crowd sourced and cannot be considered to be exhaustive
  types:
    - polygons
  select:
    - name
    - building
    - building:levels
    - building:materials
    - addr:full
    - addr:housenumber
    - addr:street
    - addr:city
    - office
    - source
  where: building IS NOT NULL

Roads:
  hdx:
    tags: roads, transportation, geodata
    caveats: OpenStreetMap data is crowd sourced and cannot be considered to be exhaustive
  types:
    - lines
    - polygons
  select:
    - name
    - highway
    - surface
    - smoothness
    - width
    - lanes
    - oneway
    - bridge
    - layer
    - source
  where: highway IS NOT NULL

Waterways:
  hdx:
    tags: rivers, water bodies - hydrography, geodata
    caveats: OpenStreetMap data is crowd sourced and cannot be considered to be exhaustive
  types:
    - lines
    - polygons
  select:
    - name
    - waterway
    - covered
    - width
    - depth
    - layer
    - blockage
    - tunnel
    - natural
    - water
    - source
  where: waterway IS NOT NULL OR water IS NOT NULL OR natural IN ('water','wetland','bay')

Points of Interest:
  hdx:
    tags: facilities and infrastructure, points of interest - poi, geodata
    caveats: OpenStreetMap data is crowd sourced and cannot be considered to be exhaustive
  types:
    - points
    - polygons
  select:
    - name
    - amenity
    - man_made
    - shop
    - tourism
    - opening_hours
    - beds
    - rooms
    - addr:full
    - addr:housenumber
    - addr:street
    - addr:city
    - source
  where: amenity IS NOT NULL OR man_made IS NOT NULL OR shop IS NOT NULL OR tourism IS NOT NULL

Airports:
  hdx:
    tags: airports, helicopter landing zone - hlz, aviation, facilities and infrastructure, transportation, geodata
    caveats: OpenStreetMap data is crowd sourced and cannot be considered to be exhaustive
  types:
    - points
    - lines
    - polygons
  select:
    - name
    - aeroway
    - building
    - emergency
    - emergency:helipad
    - operator:type
    - capacity:persons
    - addr:full
    - addr:city
    - source
  where: aeroway IS NOT NULL OR building = 'aerodrome' OR emergency:helipad IS NOT NULL OR emergency = 'landing_site'


Sea Ports:
    hdx:
      tags: ports, logistics, facilities and infrastructure, transportation, geodata
      caveats: OpenStreetMap data is crowd sourced and cannot be considered to be exhaustive
    types:
      - points
      - lines
      - polygons
    select:
      - name
      - amenity
      - building
      - port
      - operator:type
      - addr:full
      - addr:city
      - source
    where: amenity = 'ferry_terminal' OR building = 'ferry_terminal' OR port IS NOT NULL

Education Facilities:
  hdx:
    tags: education facilities - schools, education, geodata
    caveats: OpenStreetMap data is crowd sourced and cannot be considered to be exhaustive
  types:
    - points
    - polygons
  select:
    - name
    - amenity
    - building
    - operator:type
    - capacity:persons
    - addr:full
    - addr:city
    - source
  where: amenity IN ('kindergarten', 'school', 'college', 'university') OR building IN ('kindergarten', 'school', 'college', 'university')

Health Facilities:
  hdx:
    tags: health facilities, health, geodata
    caveats: OpenStreetMap data is crowd sourced and cannot be considered to be exhaustive
  types:
    - points
    - polygons
  select:
    - name
    - amenity
    - building
    - healthcare
    - healthcare:speciality
    - operator:type
    - capacity:persons
    - addr:full
    - addr:city
    - source
  where: healthcare IS NOT NULL OR amenity IN ('doctors', 'dentist', 'clinic', 'hospital', 'pharmacy')

Populated Places:
  hdx:
    tags: populated places - settlements, geodata
    caveats: OpenStreetMap data is crowd sourced and cannot be considered to be exhaustive
  types:
    - points
    - polygons
  select:
    - name
    - place
    - population
    - is_in
    - source
  where: place IN ('isolated_dwelling', 'town', 'village', 'hamlet', 'city')

Financial Services:
    hdx:
      tags: financial institutions, services, geodata
      caveats: OpenStreetMap data is crowd sourced and cannot be considered to be exhaustive
    types:
      - points
      - polygons
    select:
      - name
      - amenity
      - operator
      - network
      - addr:full
      - addr:city
      - source
    where: amenity IN ('mobile_money_agent','bureau_de_change','bank','microfinance','atm','sacco','money_transfer','post_office')


Railways:
  hdx:
    tags: facilities and infrastructure,railways,transportation, geodata
    caveats: OpenStreetMap data is crowd sourced and cannot be considered to be exhaustive
  types:
    - lines
    - points
    - polygons
  select:
    - name
    - railway
    - ele
    - operator:type
    - layer
    - addr:full
    - addr:city
    - source
  where: railway IN ('rail','subway','station')
"""

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for region in HDXExportRegion.objects.all():
            job = region.job
            job.feature_selection = NEW_YAML
            job.save()
