# -*- coding: utf-8 -*-
from collections import OrderedDict

t = {
    'Building digitizing': [
            {'Building':'building:yes'}
    ],
    'Building feature': [
            {'Housenumber' : 'addr:housenumber'},
            {'Housename' : 'addr:housename' },
            {'Street' : 'addr:street' },
    ],
    'Place':{
        'Places':[
            { 'name': 'City', 'tag': 'place:city', 'geom': ['node','area']},
            {'Town': 'place:town'},
            {'Suburb': 'place:suburb'},
            {'Neighborhood': 'place:neighbourhood'},
            {'Village': 'place:village'},
            {'Hamlet': 'place:hamlet'},
            {'Isolated Dwelling': 'place:isolated_dwelling'},
            {'Locality': 'place:locality'}
        ],
    },
    'Transportation':{
        'Roads':[
            'Roads and streets','Roads under construction','Paths'
        ],
        'Other road objects':[
            'Parking', 'Car Park', 'Parking entrance', 'Motorcycle Parking', 'Bicycle Parking', 'Roundabout'
            'Mini-roundabout', 'Turning Circle', 'Bridge', 'Tunnel', 'Ford', 'Fire Hydrant', 'Traffic Signal',
            'Stop', 'Pedestrian Crossing', 'Traffic Calming','Passing Place'
        ],
        'Transportation means':[
            'Bus Station','Bus Stop','Bus Platform','Taxi','Airport','Airport Ground','Helipad','Runway',
            'Taxiway','Apron','Hangar','Terminal','Gate','Road Restrictions','Road Practicability'
        ],
        'Barriers':[
            'Toll Booth', 'Border Control', 'Bollard', 'Spikes', 'Hedge', 'Fence', 'Wall', 'City Wall',
            'Retaining Wall', 'Entrance', 'Gate', 'Obstacles'
        ],
    },
    'Utilities':{
        'Water and sanitation':[
            'Drinking Water', 'Water Well', 'Spring', 'Pipeline', 'Water Storage', 'Water Tower',
            'Water Works', 'Showers', 'Toilets and latrines', 'Wastewater Plant', 'Watermill', 'Water Canals',
            'Wastewater canal', 'Damage prone'
        ],
        'Power':[
            'Power Generator','Power Station','Power Sub Station','Cable Distribution Cabinet',
            'Power Tower','Pole','Power Line','Street Lamp'
        ],
        'Solid waste management':[
            'Landill', 'Recycling', 'Waste Disposal', 'Waste Basket'
        ],
        'Telecommunication':[
            'Radio or TV studio','Telecommunication antenna'
        ]
    },
    'Cultural and social':{
        'Place of worship':[
            'Place of worship','Graveyard'
        ],
        'Community Center': [
            'Community Centre',
        ],
        'Culture':[
            'Museum','Cinema','Theatre','Library','Arts Centre','Artwork'
        ],
        'Historic Places':[
            'Castle','Monument','Memorial'
        ],
        'Sport Facilities':[
            'Pitch','Stadium','Sports Centre','Racetrack','Golf Course','Miniature Golf','Bench'
        ]
    },
    'Public services': {
        'Educational facilities':[
            'Kindergarten','School','College','University'
        ],
        'Health facilities':[
            'Hospital','Clinic','Doctors','Dentist','Pharmacy','Hearing Aids','Baby Hatch','Veterinary'
        ],
        'Social Facility':[
            'Ambulatory Care','Assisted Living','Workshop','Food bank','Healthcare','Shelter','Outreach','Group Home'
        ],
        'Public and government facilities':[
            'Town hall','Courthouse','Customs','Embassy','Prison','Police','Fire Station','Post Office','Post Box'
        ]
    },
    'Commercial and Economic':{
        'Accommodation':[
            'Hotel','Motel','Guest House','Hostel','Alpine Hut','Caravan Site','Camping Site'
        ],
        'Food+Drinks':[
            'Restaurant', 'Fast Food', 'Food Court', 'Cafe', 'Pub', 'Biergarten', 'Bar', 'Nightclub','Brothel'
        ],
        'Tourism':[
            'Beach resort','Attraction','Viewpoint','Information Office','Map','Information Board'
        ],
        'Food':[
            'Supermarket','Convenience Store','Kiosk','Baker','Butcher','Seafood',
            'Deli (Fine Food)','Confectionery','Marketplace','Greengrocer','Alcohol','Beverages'
        ],
        'Clothes':[
            'Clothes','Boutique','Shoes','Outdoor','Sports','Dry Cleaning','Laundry','Tailor','Fabric'
        ],
        'Electronic':[
            'Computer','Internet cafe','Electronics','Mobile Phone','Vacuum Cleaner','Hifi','Video'
        ],
        'Vehicles':[
            'Car','Fuel','Wash','Car Dealer','Repair','Car parts','Tyres','Rental','Sharing','Motorcycle',
            'Motorcycle Dealer','Bicycle','Bike Dealer','Rental'
        ],
        'Cash':[
            'Bank','Money Transfer','Money Exchange','Automated Teller Machine','Lottery kiosk','Pawnbroker'
        ],
        'Other':[
            'Department Store','Mall','Chemist','Hairdresser','Beauty','Optician','Jewelry','Erotic',
            'Florist','Garden Centre','Funeral directors','Hardware','Trade','Glaziery','Paint','Furniture',
            'Kitchen','Curtain','Frame','Stationery','Copyshop','Book Store','Photo Shop','Recording Studio',
            'Travel Agency','Musical Instrument','Toys','Variety Store'
        ],
        'Craft':[
            'Basket maker','Beekeeper','Blacksmith','Bookbinder','Brewery','Carpenter','Clockmaker',
            'Distillery','Key cutter','Pottery','Saddler','Shoemaker','Stonemason','Upholsterer'
        ],
        'Offices':[
            'Employment Agency','Architect','Government','Administration','Foundation','Research',
            'Estate Agent','IT Specialist','Non Government Organisation','Quango','Private Company',
            'Lawyer','Travel Agent','Accountant','Telecommunication','Insurance','Newspaper',
            'Information centre','Works'
        ]
    },
    # fix this..
    'Landuse':{
        'Various':[
            'Built urban','Marketplace','Agricultural','Salt Pond','Reservoir','Cemetery',
            'Fenced/walled area',
        ],
        'Leisure':[
            'Park','Garden','Playground'
        ],
    },

    'Physical environment':{
        'Nature':[
            'Peak','Tree','Wood','Forest','Nature Reserve','Scree','Fell','Scrub','Heath'
        ],
        'Water':[
            'Water','River','Stream','Spring','Waterfall','Wetland','Mud','Beach','Bay','Cliff'
        ]
    },
    'Hazards':{
        'Hazadous Areas':[
            'Flood prone','Landslide prone','Windstorm prone'
        ]
    }
}


tags =  {
    'Building digitizing': [],
    'Building feature': [],
    'Place':{
        'Places':[
            'City','Town','Suburb','Neighborhood','Village','Hamlet','Isolated Dwelling','Locality'
        ],
    },
    'Transportation':{
        'Roads':[
            'Roads and streets','Roads under construction','Paths'
        ],
        'Other road objects':[
            'Parking', 'Car Park', 'Parking entrance', 'Motorcycle Parking', 'Bicycle Parking', 'Roundabout'
            'Mini-roundabout', 'Turning Circle', 'Bridge', 'Tunnel', 'Ford', 'Fire Hydrant', 'Traffic Signal',
            'Stop', 'Pedestrian Crossing', 'Traffic Calming','Passing Place'
        ],
        'Transportation means':[
            'Bus Station','Bus Stop','Bus Platform','Taxi','Airport','Airport Ground','Helipad','Runway',
            'Taxiway','Apron','Hangar','Terminal','Gate','Road Restrictions','Road Practicability'
        ],
        'Barriers':[
            'Toll Booth', 'Border Control', 'Bollard', 'Spikes', 'Hedge', 'Fence', 'Wall', 'City Wall',
            'Retaining Wall', 'Entrance', 'Gate', 'Obstacles'
        ],
    },
    'Utilities':{
        'Water and sanitation':[
            'Drinking Water', 'Water Well', 'Spring', 'Pipeline', 'Water Storage', 'Water Tower',
            'Water Works', 'Showers', 'Toilets and latrines', 'Wastewater Plant', 'Watermill', 'Water Canals',
            'Wastewater canal', 'Damage prone'
        ],
        'Power':[
            'Power Generator','Power Station','Power Sub Station','Cable Distribution Cabinet',
            'Power Tower','Pole','Power Line','Street Lamp'
        ],
        'Solid waste management':[
            'Landill', 'Recycling', 'Waste Disposal', 'Waste Basket'
        ],
        'Telecommunication':[
            'Radio or TV studio','Telecommunication antenna'
        ]
    },
    'Cultural and social':{
        'Place of worship':[
            'Place of worship','Graveyard'
        ],
        'Community Center': [
            'Community Centre',
        ],
        'Culture':[
            'Museum','Cinema','Theatre','Library','Arts Centre','Artwork'
        ],
        'Historic Places':[
            'Castle','Monument','Memorial'
        ],
        'Sport Facilities':[
            'Pitch','Stadium','Sports Centre','Racetrack','Golf Course','Miniature Golf','Bench'
        ]
    },
    'Public services': {
        'Educational facilities':[
            'Kindergarten','School','College','University'
        ],
        'Health facilities':[
            'Hospital','Clinic','Doctors','Dentist','Pharmacy','Hearing Aids','Baby Hatch','Veterinary'
        ],
        'Social Facility':[
            'Ambulatory Care','Assisted Living','Workshop','Food bank','Healthcare','Shelter','Outreach','Group Home'
        ],
        'Public and government facilities':[
            'Town hall','Courthouse','Customs','Embassy','Prison','Police','Fire Station','Post Office','Post Box'
        ]
    },
    'Commercial and Economic':{
        'Accommodation':[
            'Hotel','Motel','Guest House','Hostel','Alpine Hut','Caravan Site','Camping Site'
        ],
        'Food+Drinks':[
            'Restaurant', 'Fast Food', 'Food Court', 'Cafe', 'Pub', 'Biergarten', 'Bar', 'Nightclub','Brothel'
        ],
        'Tourism':[
            'Beach resort','Attraction','Viewpoint','Information Office','Map','Information Board'
        ],
        'Food':[
            'Supermarket','Convenience Store','Kiosk','Baker','Butcher','Seafood',
            'Deli (Fine Food)','Confectionery','Marketplace','Greengrocer','Alcohol','Beverages'
        ],
        'Clothes':[
            'Clothes','Boutique','Shoes','Outdoor','Sports','Dry Cleaning','Laundry','Tailor','Fabric'
        ],
        'Electronic':[
            'Computer','Internet cafe','Electronics','Mobile Phone','Vacuum Cleaner','Hifi','Video'
        ],
        'Vehicles':[
            'Car','Fuel','Wash','Car Dealer','Repair','Car parts','Tyres','Rental','Sharing','Motorcycle',
            'Motorcycle Dealer','Bicycle','Bike Dealer','Rental'
        ],
        'Cash':[
            'Bank','Money Transfer','Money Exchange','Automated Teller Machine','Lottery kiosk','Pawnbroker'
        ],
        'Other':[
            'Department Store','Mall','Chemist','Hairdresser','Beauty','Optician','Jewelry','Erotic',
            'Florist','Garden Centre','Funeral directors','Hardware','Trade','Glaziery','Paint','Furniture',
            'Kitchen','Curtain','Frame','Stationery','Copyshop','Book Store','Photo Shop','Recording Studio',
            'Travel Agency','Musical Instrument','Toys','Variety Store'
        ],
        'Craft':[
            'Basket maker','Beekeeper','Blacksmith','Bookbinder','Brewery','Carpenter','Clockmaker',
            'Distillery','Key cutter','Pottery','Saddler','Shoemaker','Stonemason','Upholsterer'
        ],
        'Offices':[
            'Employment Agency','Architect','Government','Administration','Foundation','Research',
            'Estate Agent','IT Specialist','Non Government Organisation','Quango','Private Company',
            'Lawyer','Travel Agent','Accountant','Telecommunication','Insurance','Newspaper',
            'Information centre','Works'
        ]
    },
    # fix this..
    'Landuse':{
        'Various':[
            'Built urban','Marketplace','Agricultural','Salt Pond','Reservoir','Cemetery',
            'Fenced/walled area',
        ],
        'Leisure':[
            'Park','Garden','Playground'
        ],
    },

    'Physical environment':{
        'Nature':[
            'Peak','Tree','Wood','Forest','Nature Reserve','Scree','Fell','Scrub','Heath'
        ],
        'Water':[
            'Water','River','Stream','Spring','Waterfall','Wetland','Mud','Beach','Bay','Cliff'
        ]
    },
    'Hazards':{
        'Hazadous Areas':[
            'Flood prone','Landslide prone','Windstorm prone'
        ]
    }
}

HOT_HDM = OrderedDict(sorted(t.items()))
