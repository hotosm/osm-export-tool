# -*- coding: utf-8 -*-
from collections import OrderedDict

tags = {
    'Aerialway': [],
    'Aeroway': [],
    'Amenity': {
        '': [
        'Sustenance', 'Education', 'Transportation', 'Financial', 'Healthcare',
        'Entertainment, Arts & Culture', 'Others'
    ],
    },
    'Barrier': [
        'Linear Barriers', 'Access Control on Highways'
    ],
    'Boundary': [
        'Attributes'
    ],
    'Building': [
        'Accommodation', 'Commercial', 'Civic/Amenity', 'Other Buildings', 'Additional Attributes'
    ],
    'Craft': [],
    'Emergency': [
        'Medical Rescue', 'Firefighters', 'Lifeguards', 'Others'
    ],
    'Geological': [],
    'Highway': [
        'Roads', 'Link roads', 'Special road types', 'Paths', 'Lifecycle', 'Attributes', 'Other highway features'
    ],
    'Historic': [],
    'Landuse': [],
    'Leisure': [],
    'Man Made': [],
    'Military': [],
    'Natural': [
        'Vegetation or surface related', 'Water related', 'Landform related'
    ],
    'Office': [],
    'Places': [
        'Administratively declared places', 'Populated settlements, urban', 'Populated settlements, urban and rural',
        'Other places', 'Additional attributes'
    ],
    'Power': [],
    'Public Transport': [],
    'Railway': [
        'Tracks', 'Additional features', 'Stations and Stops', 'Other railways'
    ],
    'Route': [],
    'Shop': [
        'Food, beverages', 'General store, department store, mall', 'Clothing, shoes, accessories',
        'Discount store, charity', 'Health and beauty', 'Do-it-yourself, household, building materials, gardening',
        'Furniture and interior', 'Electronics', 'Outdoors and sport, vehicles', 'Art, music, hobbies',
        'Stationery, gifts, books, newspapers', 'Others'
    ],
    'Sport': [],
    'Tourism': [],
    'Waterway': [
        'Natural watercourses', 'Man made waterways', 'Facilities', 'Barriers on waterways',
        'Other features on waterways', 'Some additional attributes for waterways'
    ],
    'Addresses': [
        'Tags for individual houses', 'For countries using hamlet, subdistrict, district, province, state',
        'Tags for interpolation ways'
    ],
    'Annotation': [],
    'Name': [],
    'Properties': [],
    'References': [],
    'Restrictions': []
}

OSM_DM = OrderedDict(sorted(tags.items()))
