import csv
import json

# headers = ['standid', 'fortype', 'year', 'climate', 'rx']

climates = []
years = []
types = []
data = {}
links = {}
stands = {}
sankey_data = {
    'nodes':[],
    'links':[]
}

forest_type_map = {
    '183': {
        "name": 'Western Juniper',
        "category": 'Pinyon-juniper'
    },
    '201': {
        "name": 'Douglas-fir',
        "category": 'Douglas-fir'
    },
    '202': {
        "name": 'Port Orford cedar',
        "category": 'Douglas-fir'
    },
    '221': {
        "name": 'Ponderosa pine',
        "category": 'Ponderosa pine'
    },
    '222': {
        "name": 'Incense cedar',
        "category": 'Ponderosa pine'
    },
    '223': {
        "name": 'Jeffrey-Coulter-Bigcone Douglas-fir',
        "category": 'Ponderosa pine'
    },
    '224': {
        "name": 'Sugar pine',
        "category": 'Ponderosa pine'
    },
    '241': {
        "name": 'Western white pine',
        "category": 'Western white pine'
    },
    '261': {
        "name": 'White fir',
        "category": 'Fir-spruce-Mountain hemlock'
    },
    '262': {
        "name": 'Red fir',
        "category": 'Fir-spruce-Mountain hemlock'
    },
    '263': {
        "name": 'Noble fir',
        "category": 'Fir-spruce-Mountain hemlock'
    },
    '264': {
        "name": 'Pacific silver fir',
        "category": 'Fir-spruce-Mountain hemlock'
    },
    '267': {
        "name": 'Grand fir',
        "category": 'Fir-spruce-Mountain hemlock'
    },
    '268': {
        "name": 'Subalpine fir',
        "category": 'Fir-spruce-Mountain hemlock'
    },
    '281': {
        "name": 'Lodgepole pine',
        "category": 'Lodgepole pine'
    },
    '301': {
        "name": 'Western hemlock',
        "category": 'Hemlock-Sitka spruce'
    },
    '304': {
        "name": 'Western redcedar',
        "category": 'Hemlock-Sitka spruce'
    },
    '305': {
        "name": 'Sitka spruce',
        "category": 'Hemlock-Sitka spruce'
    },
    '361': {
        "name": 'Knobcone pine',
        "category": 'Other western softwoods'
    },
    '702': {
        "name": 'River birch-sycamore',
        "category": 'Elm-ash-cottonwood'
    },
    '703': {
        "name": 'Cottonwood',
        "category": 'Elm-ash-cottonwood'
    },
    '704': {
        "name": 'Willow',
        "category": 'Elm-ash-cottonwood'
    },
    '709': {
        "name": 'Cottonwood-willow',
        "category": 'Elm-ash-cottonwood'
    },
    '722': {
        "name": 'Oregon ash',
        "category": 'Elm-ash-cottonwood'
    },
    '901': {
        "name": 'Aspen',
        "category": 'Aspen-birch'
    },
    '911': {
        "name": 'Red alder',
        "category": 'Alder-maple'
    },
    '912': {
        "name": 'Bigleaf maple',
        "category": 'Alder-maple'
    },
    '922': {
        "name": 'California black oak',
        "category": 'Western oak'
    },
    '923': {
        "name": 'Oregon white oak',
        "category": 'Western oak'
    },
    '924': {
        "name": 'Blue oak',
        "category": 'Western oak'
    },
    '925': {
        "name": 'Deciduous oak woodland',
        "category": 'Western oak'
    },
    '932': {
        "name": 'Canyon-interior live oak',
        "category": 'Western oak'
    },
    '941': {
        "name": 'Tan oak',
        "category": 'Tanoak-laurel'
    },
    '942': {
        "name": 'California laurel',
        "category": 'Tanoak-laurel'
    },
    '943': {
        "name": 'Giant chinkapin',
        "category": 'Tanoak-laurel'
    },
    '951': {
        "name": 'Pacific madrone',
        "category": 'Other western hardwoods'
    },
    '953': {
        "name": 'Mountain brush woodland',
        "category": 'Other western hardwoods'
    },
    '996': {
        "name": 'FVS other softwoods',
        "category": 'FVS types'
    },
    '997': {
        "name": 'FVS other hardwoods',
        "category": 'FVS types'
    },
    '998': {
        "name": 'FVS other species',
        "category": 'FVS types'
    },
    '999': {
        "name": 'Nonstocked',
        "category": 'Nonstocked'
    }
}

# organize_stands_by = 'name'
organize_stands_by = 'category'
year_type_delimiter = "#"

with open('data/forest_type_climate_change_sankey.csv', 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        climate = row['climate']
        if not row['climate'] in climates:
            climates.append(climate)
            data[climate] = {}
        if not int(row['year']) in years:
            years.append(int(row['year']))
            years.sort()
        if not row['fortype'] in types:
            types.append(row['fortype'])

        if not data[climate].has_key(str(row['standid'])):
            data[climate][str(row['standid'])] = {}

        data[climate][str(row['standid'])][str(row['year'])] = forest_type_map[row['fortype']][organize_stands_by]

        if not stands.has_key(str(row['standid'])):
            stands[str(row['standid'])] = {'acres': float(row['acres'])}

for climate_key in data.keys():
    climate = data[climate_key]
    climate['links'] = {}
    for stand_key in climate.keys():
        if stand_key != 'links':
            stand = climate[stand_key]
            for index, year in enumerate(years):
                if not index == 0:
                    from_type = stand[str(years[index-1])]
                    to_type = stand[str(year)]

                    if not climate['links'].has_key(str(year)):
                        climate['links'][str(year)] = {}
                    if not climate['links'][str(year)].has_key(str(from_type)):
                        climate['links'][str(year)][str(from_type)] = {}
                    if not climate['links'][str(year)][str(from_type)].has_key(str(to_type)):
                        climate['links'][str(year)][str(from_type)][str(to_type)] = 0

                    climate['links'][str(year)][str(from_type)][str(to_type)] += stands[stand_key]['acres']

    year_types = []
    for index, to_year in enumerate(years[1:]): #initial year not captured in links as a key
        for from_type in climate['links'][str(to_year)].keys():
            from_year = years[years.index(to_year)-1]
            from_year_type = "%s%s%s" % (str(from_year), year_type_delimiter, str(from_type))
            if from_year_type not in year_types:
                year_types.append(from_year_type)
            for to_type in climate['links'][str(to_year)][from_type].keys():
                to_year_type = "%s%s%s" % (str(to_year), year_type_delimiter, str(to_type))
                if to_year_type not in year_types:
                    year_types.append(to_year_type)

    climate['sankey_data'] = {
        "nodes": [{"name":str(x)} for x in year_types],
        "links": []
    }
    for idx, from_year_type in enumerate(year_types):
        from_year, from_type = from_year_type.split(year_type_delimiter)

        for to_year_type in year_types:
            to_year, to_type = to_year_type.split(year_type_delimiter)
            if years.index(int(from_year)) == years.index(int(to_year))-1 and climate['links'][str(to_year)].has_key(str(from_type)) and climate['links'][str(to_year)][str(from_type)].has_key(str(to_type)):
                climate['sankey_data']['links'].append(
                    {
                        "source": idx, 
                        "target": year_types.index(to_year_type),
                        "value": climate['links'][str(to_year)][str(from_type)][str(to_type)]
                    }
                )

    with open('results/%s-fortype.json' % climate_key, 'w') as outfile:
        json.dump(climate['sankey_data'], outfile)

    with open('/usr/local/apps/d3test/%s-fortype.json' % climate_key, 'w') as outfile:
        json.dump(climate['sankey_data'], outfile)

