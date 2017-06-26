export const TAGTREE = {
    "Commerce": {
        "children": {
            "Finance": {
                "search_terms": "bank,atm,money"
            },
            "Shops & Markets": {},
            "Tourism": {},
            "Accommodation": {
                "search_terms": "hotel,hostel,motel"
            }
        }
    },
    "Health, Emergency and Sanitation": {
        "children": {
            "Police and Fire Stations": {},
            "Drinking Water": {
                "search_terms": "water,pump,well"
            },
            "Fire Hydrants and Defibrillators": {},
            "Public Toilets": {},
            "Health Facilities": {
                "search_terms": "clinic,doctor,pharmacy,hospital,dentist"
            }
        }
    },
    "Public Institutions, Government and Offices": {
        "children": {
            "Educational Facilities": {
                "search_terms": "school,college,university"
            },
            "Places of Worship": {
                "search_terms": "church,mosque,synagogue,religion,religious"
            },
            "Government": {
                "search_terms": "court,town hall"
            },
            "Offices": {},
            "Embassies": {
                "search_terms": "embassy"
            },
            "Military": {},
            "Community Centres": {}
        }
    },
    "Transportation": {
        "children": {
            "Gas Stations": {
                "search_terms": "fuel"
            },
            "All Transit Stations": {
                "search_terms": "transport"
            },
            "Roads": {},
            "Footpaths": {
                "search_terms": "trail"
            },
            "Bus Stations": {},
            "Rail Stations": {
                "search_terms": "train"
            },
            "Rail": {
                "search_terms": "train"
            },
            "Ferry": {
                "search_terms": "boat"
            },
            "Airports": {}
        }
    },
    "Buildings": {
        "children": {
            "All Buildings": {},
            "Building Addresses": {}
        }
    },
    "Localities": {
        "children": {
            "Administrative Boundaries": {
                "search_terms": "border"
            },
            "Places": {
                "search_terms": "population"
            }
        }
    },
    "Infrastructure": {
        "children": {
            "Communication": {
                "search_terms": "tower"
            },
            "Water Supply Systems": {
                "search_terms": "pump"
            },
            "Solid Waste": {
                "search_terms": "dump,landfill"
            },
            "Drainage": {
                "search_terms": "ditch"
            },
            "Power Systems": {
                "search_terms": "electricity"
            },
            "Backup Generators": {
                "search_terms": "electricity"
            },
            "Storage Warehouse": {}
        }
    },
    "Sport and Recreation": {
        "children": {
            "Stadiums": {
                "search_terms": "arena"
            },
            "Swimming Pools": {},
            "Pitch": {
                "search_terms": "field,court"
            },
            "Sport Centres": {}
        }
    },
    "Land Use": {
        "children": {
            "Cemetaries": {
                "search_terms": "graveyard"
            },
            "Brownfields and Greenfields": {},
            "Parks": {}
        }
    },
    "Natural": {
        "children": {
            "Bodies of Water": {
                "search_terms": "lakes,ponds,rivers,streams"
            },
            "Coastlines": {},
            "Wetlands": {}
        }
    },
    "Humanitarian": {
        "children": {
            "Refugee Facilities": {},
            "Building Materials and Conditions": {}
        }
    },
    "Languages": {
        "children": {
            "Default": {},
            "English": {},
            "Swahili": {},
            "French": {}
        }
    }
}
export const TAGLOOKUP = {
    "Finance": {
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
        "where": "amenity IN ('atm','bank','microfinance','mobile_money_agent','money_transfer')"
    },
    "Shops & Markets": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "opening_hours",
            "shop"
        ],
        "where": "shop IS NOT NULL or amenity='marketplace'"
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
    "Police and Fire Stations": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "amenity",
            "building"
        ],
        "where": "amenity IN ('police','fire_station')"
    },
    "Drinking Water": {
        "geom_types": [
            "point"
        ],
        "keys": [
            "name",
            "amenity",
            "pump",
            "man_made"
        ],
        "where": "amenity='water_point' or pump is not null or man_made='well'"
    },
    "Fire Hydrants and Defibrillators": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "emergency",
            "fire_hydrant:type"
        ],
        "where": "emergency IN ('fire_hydrant','defibrillator')"
    },
    "Public Toilets": {
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
        "where": "amenity='toilets'"
    },
    "Health Facilities": {
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
        "where": "amenity IN ('clinic','doctors','hospital','pharmacy','dentist')"
    },
    "Educational Facilities": {
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
        "where": "amenity IN ('college','kindergarten','school','university')"
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
    "Government": {
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
    "Offices": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "office",
            "name",
            "operator"
        ],
        "where": "office IS NOT NULL"
    },
    "Embassies": {
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
    "Community Centres": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "amenity",
            "community_centre",
            "name",
            "opening_hours"
        ],
        "where": "amenity='community_centre'"
    },
    "Gas Stations": {
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
    "All Transit Stations": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "public_transport",
            "operator",
            "building",
            "amenity"
        ],
        "where": "public_transport IS NOT NULL"
    },
    "Roads": {
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
    "Footpaths": {
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
    "Bus Stations": {
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
    "Rail Stations": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "building",
            "railway",
            "public_transport",
            "operator"
        ],
        "where": "railway='station' OR building='train_station'"
    },
    "Rail": {
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
    "Ferry": {
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
    "Airports": {
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
    "All Buildings": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "building",
            "name",
            "building:levels"
        ],
        "where": "building IS NOT NULL"
    },
    "Building Addresses": {
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
    "Administrative Boundaries": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "admin_level",
            "boundary",
            "name",
            "is_in"
        ],
        "where": "boundary IS NOT NULL"
    },
    "Places": {
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
        "where": "place IS NOT NULL"
    },
    "Communication": {
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
    "Water Supply Systems": {
        "geom_types": [
            "point",
            "line",
            "polygon"
        ],
        "keys": [
            "man_made"
        ],
        "where": "man_made IN ('water_tower', 'pumping_station') OR building='pumping_station' OR landuse='reservoir' or waterway='floodgate'"
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
    "Power Systems": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "power"
        ],
        "where": "power IS NOT NULL OR building='power_plant'"
    },
    "Backup Generators": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "backup_generator"
        ],
        "where": "backup_generator IS NOT NULL"
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
    "Stadiums": {
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
    "Swimming Pools": {
        "geom_types": [
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
    "Sport Centres": {
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
    "Cemetaries": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "name",
            "amenity"
        ],
        "where": "amenity='grave_yard'"
    },
    "Brownfields and Greenfields": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "landuse"
        ],
        "where": "landuse IN ('brownfield','greenfield')"
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
    "Bodies of Water": {
        "geom_types": [
            "line",
            "polygon"
        ],
        "keys": [
            "water",
            "waterway",
            "natural"
        ],
        "where": "waterway IS NOT NULL OR water IS NOT NULL OR natural IN ('water','bay')"
    },
    "Coastlines": {
        "geom_types": [
            "line"
        ],
        "keys": [
            "natural"
        ],
        "where": "natural='coastline'"
    },
    "Wetlands": {
        "geom_types": [
            "polygon"
        ],
        "keys": [
            "natural"
        ],
        "where": "natural='wetland'"
    },
    "Refugee Facilities": {
        "geom_types": [
            "point",
            "polygon"
        ],
        "keys": [
            "name",
            "social_facility"
        ],
        "where": "social_facility='shelter'"
    },
    "Building Materials and Conditions": {
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
