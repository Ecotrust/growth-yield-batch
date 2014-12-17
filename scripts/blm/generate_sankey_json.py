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

        data[climate][str(row['standid'])][str(row['year'])] = row['fortype']

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
    for type in types:
        for year in years:
            year_types.append("%s-%s" % (str(year), str(type)))
    climate['sankey_data'] = {
        "nodes": [{"name":str(x)} for x in year_types],
        "links": []
    }
    for idx, from_year_type in enumerate(year_types):
        from_year, from_type = from_year_type.split('-')

        for to_year_type in year_types:
            to_year, to_type = to_year_type.split('-')
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

