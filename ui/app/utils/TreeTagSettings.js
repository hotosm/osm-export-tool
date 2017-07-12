export const TAGTREE = {
    "Building": {
        "children": {
            "Building*": {},
            "Addresses": {},
            "Materials and Condition": {}
        }
    },
    "Commercial": {
        "children": {
            "Commercial*": {},
            "Shop": {},
            "Supermarket": {},
            "Restaurant": {},
            "Tourism": {},
            "Accommodation": {}
        }
    },
    "Communication": {
        "children": {
            "Communication*": {},
            "Communication Tower": {}
        }
    },
    "Education": {
        "children": {
            "Education*": {},
            "Kindergarten": {},
            "School": {},
            "College": {},
            "University": {}
        }
    },
    "Emergency": {
        "children": {
            "Emergency*": {},
            "Police Station": {},
            "Ambulance Station": {},
            "Fire Station": {}
        }
    },
    "Financial": {
        "children": {
            "Financial*": {},
            "ATM": {},
            "Bank": {},
            "Bureau de Change": {}
        }
    },
    "Government": {
        "children": {
            "Government*": {},
            "Government Office": {},
            "Embassy": {},
            "Military": {},
            "Post Office": {}
        }
    },
    "Healthcare": {
        "children": {
            "Healthcare*": {},
            "Doctor": {},
            "Dentist": {},
            "Clinic": {},
            "Hospital": {},
            "Pharmacy": {},
            "Alternative": {}
        }
    },
    "Humanitarian": {
        "children": {
            "Humanitarian*": {},
            "Wheelchair Access": {},
            "Refugee Facility": {},
            "Storage Warehouse": {}
        }
    },
    "Land Use": {
        "children": {
            "All Land Use*": {},
            "Parks": {},
            "Cemetary": {},
            "Residential": {},
            "Agriculture": {},
            "Solid Waste": {}
        }
    },
    "Localities": {
        "children": {
            "Localities*": {},
            "Administrative Boundary": {},
            "Place": {},
            "Postcode": {}
        }
    },
    "Natural": {
        "children": {
            "Natural*": {},
            "Coastline": {},
            "Water Body": {},
            "Forest": {},
            "Grassland": {},
            "Wetland": {},
            "Landform": {}
        }
    },
    "Power": {
        "children": {
            "Power*": {},
            "Electricial Tower": {},
            "Substation": {},
            "Power Plant": {},
            "Backup Generator": {},
            "Gas Station": {}
        }
    },
    "Public": {
        "children": {
            "Public*": {},
            "Places of Worship": {},
            "Community Centre": {},
            "Library": {},
            "Historic": {},
            "Toilet": {}
        }
    },
    "Sport": {
        "children": {
            "Sport*": {},
            "Stadium": {},
            "Swimming Pool": {},
            "Pitch": {},
            "Sport Centre": {}
        }
    },
    "Transportation": {
        "children": {
            "Transportation*": {},
            "Airport": {},
            "Ferry Terminal": {},
            "Train Station": {},
            "Bus Station": {},
            "Footpath": {},
            "Road": {},
            "Railway": {}
        }
    },
    "Water": {
        "children": {
            "Water*": {},
            "Dam": {},
            "Reservoir": {},
            "Floodgate": {},
            "Drainage": {},
            "Water Tower": {},
            "Pump House": {},
            "Waterway": {},
            "Water Point": {}
        }
    },
    "Language": {
        "children": {
            "Default": {},
            "English": {},
            "Swahili": {},
            "French": {}
        }
    }
}
export const TAGLOOKUP = {
    "Building*": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "building"
        ],
        "where": "building IS NOT NULL"
    },
    "Addresses": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "addr:housenumber",
            "addr:street"
        ],
        "where": ""
    },
    "Materials and Condition": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "building:material",
            "roof:material",
            "access:roof"
        ],
        "where": "building IS NOT NULL"
    },
    "Commercial*": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "shop",
            "tourism",
            "amenity"
        ],
        "where": "shop IS NOT NULL OR tourism IS NOT NULL OR amenity IN ('marketplace','restaurant','fast_food','cafe','bar','pub')"
    },
    "Shop": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "opening_hours",
            "shop"
        ],
        "where": "shop IS NOT NULL"
    },
    "Supermarket": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "opening_hours",
            "shop"
        ],
        "where": "amenity='marketplace' OR shop='convenience' OR shop='supermarket'"
    },
    "Restaurant": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity"
        ],
        "where": "amenity IN ('restaurant','fast_food','cafe','bar','pub')"
    },
    "Tourism": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "tourism"
        ],
        "where": "tourism IS NOT NULL"
    },
    "Accommodation": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "tourism",
            "rooms",
            "beds"
        ],
        "where": "tourism IN ('hotel','chalet','guest_house','hostel','motel')"
    },
    "Communication*": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "man_made",
            "tower:type",
            "office"
        ],
        "where": "man_made='communications_tower' OR \"tower:type\"='communication' OR office='telecommunication'"
    },
    "Communication Tower": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "man_made",
            "tower",
            "operator",
            "communication:mobile",
            "communication:radio"
        ],
        "where": "man_made='communications_tower' OR \"tower:type\"='communication'"
    },
    "Education*": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity",
            "office"
        ],
        "where": "amenity IN ('kindergarten', 'school', 'college', 'university','language_school') OR office='educational_institution'"
    },
    "Kindergarten": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity",
            "isced:level",
            "capacity"
        ],
        "where": "amenity='kindergarten'"
    },
    "School": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity",
            "isced:level",
            "capacity"
        ],
        "where": "amenity='school'"
    },
    "College": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity",
            "isced:level",
            "capacity"
        ],
        "where": "amenity='college'"
    },
    "University": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity",
            "isced:level",
            "capacity"
        ],
        "where": "amenity='university'"
    },
    "Emergency*": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "emergency",
            "amenity"
        ],
        "where": "emergency IS NOT NULL OR amenity IN ('police','fire_station')"
    },
    "Police Station": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity",
            "building"
        ],
        "where": "amenity='police'"
    },
    "Ambulance Station": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "emergency"
        ],
        "where": "emergency='ambulance_station'"
    },
    "Fire Station": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity"
        ],
        "where": "amenity='fire_station'"
    },
    "Financial*": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity"
        ],
        "where": "amenity IN ('atm','bank','bureau_de_change','microfinance','mobile_money_agent','money_transfer')"
    },
    "ATM": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity",
            "opening_hours",
            "operator",
            "network"
        ],
        "where": "amenity='atm'"
    },
    "Bank": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity"
        ],
        "where": "amenity='bank'"
    },
    "Bureau de Change": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity"
        ],
        "where": "amenity='bureau_de_change'"
    },
    "Government*": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "building",
            "amenity",
            "office",
            "government",
            "landuse",
            "military"
        ],
        "where": "building='civic' OR office IN ('government','political_party','notary') OR government IS NOT NULL OR landuse='military' OR military IS NOT NULL OR amenity IN ('court_house','townhall','embassy','post_office')"
    },
    "Government Office": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "building",
            "amenity",
            "office",
            "government"
        ],
        "where": "building='civic' OR amenity IN ('court_house','townhall') OR office='government' OR government IS NOT NULL"
    },
    "Embassy": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity"
        ],
        "where": "amenity='embassy'"
    },
    "Military": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "military",
            "landuse"
        ],
        "where": "military IS NOT NULL or landuse='military'"
    },
    "Post Office": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity"
        ],
        "where": "amenity='post_office'"
    },
    "Healthcare*": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity",
            "healthcare",
            "shop"
        ],
        "where": "healthcare IS NOT NULL OR amenity IN ('doctors', 'dentist', 'toilets', 'hospital', 'pharmacy') OR shop IN ('herbalist','nutrition_supplements')"
    },
    "Doctor": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "medical_system:western",
            "amenity"
        ],
        "where": "amenity='doctors'"
    },
    "Dentist": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity"
        ],
        "where": "amenity='dentist'"
    },
    "Clinic": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "opening_hours",
            "operator",
            "toilets:disposal",
            "toilets:handwashing",
            "access"
        ],
        "where": "amenity='clinic'"
    },
    "Hospital": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "medical_system:western",
            "operator",
            "health_facility:bed",
            "health_facility:level",
            "health_facility:type",
            "status",
            "staff_count:doctors",
            "staff_count:nurses",
            "opening_hours"
        ],
        "where": "amenity='hospital'"
    },
    "Pharmacy": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity"
        ],
        "where": "amenity='pharmacy'"
    },
    "Alternative": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "healthcare",
            "shop"
        ],
        "where": "healthcare='alternative' OR shop IN ('herbalist','nutrition_supplements')"
    },
    "Humanitarian*": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "building",
            "industrial",
            "social_facility"
        ],
        "where": "social_facility='shelter' OR  building='warehouse' OR industrial='warehouse'"
    },
    "Wheelchair Access": {
        "geom_types": [
            "point",
            "line",
            "polygon"
        ],
        "keys": [
            "wheelchair"
        ],
        "where": "wheelchair IS NOT NULL"
    },
    "Refugee Facility": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity",
            "social_facility"
        ],
        "where": "social_facility IS NOT NULL"
    },
    "Storage Warehouse": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "building",
            "industrial"
        ],
        "where": "building='warehouse' OR industrial='warehouse'"
    },
    "All Land Use*": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "landuse",
            "leisure",
            "amenity"
        ],
        "where": "landuse IS NOT NULL OR leisure='park' OR amenity='grave_yard'"
    },
    "Parks": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "name",
            "leisure"
        ],
        "where": "leisure='park'"
    },
    "Cemetary": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "name",
            "amenity"
        ],
        "where": "amenity='grave_yard' OR landuse='cemetery'"
    },
    "Residential": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "landuse"
        ],
        "where": "landuse='residential'"
    },
    "Agriculture": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "landuse"
        ],
        "where": "landuse IN ('farmland','farmyard','greenhouse_horticulture')"
    },
    "Solid Waste": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "landuse"
        ],
        "where": "landuse='landfill'"
    },
    "Localities*": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "boundary",
            "place",
            "addr:postcode"
        ],
        "where": "boundary IS NOT NULL OR place IS NOT NULL OR \"addr:postcode\" IS NOT NULL OR boundary='postal_code'"
    },
    "Administrative Boundary": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "admin_level",
            "boundary",
            "name",
            "is_in"
        ],
        "where": "boundary='administrative'"
    },
    "Place": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "place",
            "name",
            "is_in",
            "population"
        ],
        "where": "place IN ('country','state','region','province','district','county','municipality','city','borough','suburb','neighbourhood')"
    },
    "Postcode": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "addr:postcode",
            "boundary"
        ],
        "where": "\"addr:postcode\" IS NOT NULL OR boundary='postal_code'"
    },
    "Natural*": {
        "geom_types": [
            "point",
            "line",
            "polygon"
        ],
        "keys": [
            "natural"
        ],
        "where": "natural IS NOT NULL"
    },
    "Coastline": {
        "geom_types": [
            "line"
        ],
        "keys": [
            "natural"
        ],
        "where": "natural='coastline'"
    },
    "Water Body": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "water",
            "waterway",
            "natural"
        ],
        "where": "natural='water'"
    },
    "Forest": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "landuse"
        ],
        "where": "landuse='forest'"
    },
    "Grassland": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "natural"
        ],
        "where": "natural='grassland'"
    },
    "Wetland": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "natural"
        ],
        "where": "natural='wetland'"
    },
    "Landform": {
        "geom_types": [
            "point",
            "line",
            "polygon"
        ],
        "keys": [
            "natural"
        ],
        "where": "natural IN ('peak','volcano','valley','ridge','cliff')"
    },
    "Power*": {
        "geom_types": [
            "point",
            "tower"
        ],
        "keys": [
            "backup_generator",
            "power",
            "amenity"
        ],
        "where": "power IS NOT NULL OR backup_generator IS NOT NULL OR amenity='fuel'"
    },
    "Electricial Tower": {
        "geom_types": [
            "point"
        ],
        "keys": [
            "power"
        ],
        "where": "power='tower'"
    },
    "Substation": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "power"
        ],
        "where": "power='substation'"
    },
    "Power Plant": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "power"
        ],
        "where": "power='plant'"
    },
    "Backup Generator": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "backup_generator"
        ],
        "where": "backup_generator IS NOT NULL"
    },
    "Gas Station": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity",
            "opening_hours",
            "operator",
            "fuel"
        ],
        "where": "amenity='fuel'"
    },
    "Public*": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "building",
            "amenity",
            "historic"
        ],
        "where": "building='public' OR amenity IN ('place_of_worship','community_centre','library','toilets') OR historic IS NOT NULL"
    },
    "Places of Worship": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "building",
            "amenity",
            "religion",
            "denomination"
        ],
        "where": "amenity='place_of_worship'"
    },
    "Community Centre": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "amenity",
            "name",
            "opening_hours"
        ],
        "where": "amenity='community_centre'"
    },
    "Library": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "amenity",
            "name",
            "opening_hours"
        ],
        "where": "amenity='library'"
    },
    "Historic": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "historic"
        ],
        "where": "historic IS NOT NULL"
    },
    "Toilet": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "amenity"
        ],
        "where": "amenity='toilets'"
    },
    "Sport*": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "sport",
            "leisure"
        ],
        "where": "sport IS NOT NULL OR leisure IN ('stadium, swimming pool, pitch, sport_centre')"
    },
    "Stadium": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "name",
            "building",
            "leisure"
        ],
        "where": "leisure='stadium'"
    },
    "Swimming Pool": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "leisure"
        ],
        "where": "leisure='swimming_pool'"
    },
    "Pitch": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "name",
            "leisure"
        ],
        "where": "leisure='pitch'"
    },
    "Sport Centre": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "building",
            "leisure"
        ],
        "where": "leisure='sport_centre'"
    },
    "Transportation*": {
        "geom_types": [
            "point",
            "line",
            "polygon"
        ],
        "keys": [
            "aeroway",
            "amenity",
            "highway",
            "railway",
            "building"
        ],
        "where": "aeroway IS NOT NULL OR highway IS NOT NULL OR railway IS NOT NULL OR building IN ('aerodome','ferry_terminal','train_station') OR amenity IN ('ferry_terminal','bus_station')"
    },
    "Airport": {
        "geom_types": [
            "point",
            "line",
            "polygon"
        ],
        "keys": [
            "name",
            "building",
            "aeroway"
        ],
        "where": "aeroway IS NOT NULL OR building='aerodome'"
    },
    "Ferry Terminal": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity",
            "building"
        ],
        "where": "amenity='ferry_terminal' OR building='ferry_terminal'"
    },
    "Train Station": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "railway",
            "name",
            "layer"
        ],
        "where": "building='train_station'"
    },
    "Bus Station": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "building",
            "amenity",
            "public_transport",
            "operator"
        ],
        "where": "amenity='bus_station'"
    },
    "Footpath": {
        "geom_types": [
            "line"
        ],
        "keys": [
            "highway",
            "surface",
            "bridge",
            "tunnel",
            "layer"
        ],
        "where": "highway='footway'"
    },
    "Road": {
        "geom_types": [
            "line"
        ],
        "keys": [
            "highway",
            "name",
            "surface",
            "smoothness",
            "width",
            "oneway",
            "bridge",
            "tunnel",
            "layer"
        ],
        "where": "highway IS NOT NULL"
    },
    "Railway": {
        "geom_types": [
            "line"
        ],
        "keys": [
            "railway",
            "name",
            "layer"
        ],
        "where": "railway IS NOT NULL"
    },
    "Water*": {
        "geom_types": [
            "point",
            "line",
            "polygon"
        ],
        "keys": [
            "waterway",
            "water",
            "natural",
            "landuse",
            "man_made",
            "building"
        ],
        "where": "waterway IS NOT NULL OR water='reservoir' OR natural='water' OR landuse='reservoir' OR man_made IN ('water_tower','pumping_station') OR building='pumping_station'"
    },
    "Dam": {
        "geom_types": [
            "line",
            "polygon"
        ],
        "keys": [
            "waterway"
        ],
        "where": "waterway='dam'"
    },
    "Reservoir": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "water",
            "natural",
            "landuse"
        ],
        "where": "water='reservoir' OR natural='water' OR landuse='reservoir'"
    },
    "Floodgate": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "waterway"
        ],
        "where": "waterway='floodgate'"
    },
    "Drainage": {
        "geom_types": [
            "line"
        ],
        "keys": [
            "waterway",
            "covered",
            "blockage",
            "depth",
            "width",
            "layer",
            "diameter",
            "tunnel"
        ],
        "where": "waterway IN ('ditch','drain')"
    },
    "Water Tower": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "man_made"
        ],
        "where": "man_made='water_tower'"
    },
    "Pump House": {
        "geom_types": [
            "point",
            "line",
            "polygon"
        ],
        "keys": [
            "man_made"
        ],
        "where": "man_made='pumping_station' OR building='pumping_station'"
    },
    "Waterway": {
        "geom_types": [
            "line"
        ],
        "keys": [
            "name",
            "waterway"
        ],
        "where": "waterway IN ('river', 'canal', 'stream')"
    },
    "Water Point": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "amenity"
        ],
        "where": "amenity='water_point'"
    },
    "Default": {
        "geom_types": [
            "point",
            "line",
            "polygon"
        ],
        "keys": [
            "name"
        ],
        "where": ""
    },
    "English": {
        "geom_types": [
            "point",
            "line",
            "polygon"
        ],
        "keys": [
            "name:en"
        ],
        "where": ""
    },
    "Swahili": {
        "geom_types": [
            "point",
            "line",
            "polygon"
        ],
        "keys": [
            "name:sw"
        ],
        "where": ""
    },
    "French": {
        "geom_types": [
            "point",
            "line",
            "polygon"
        ],
        "keys": [
            "name:fr"
        ],
        "where": ""
    }
}
