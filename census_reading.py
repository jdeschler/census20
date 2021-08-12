import numpy as np
import pandas as pd
import geopandas as gpd

blocks_path = "TODO"
f1path = "TODO"
f2path = "TODO"
geopath = "TODO"
outfile = "TODO"

def main():
    blocks = gpd.read_file(blocks_path)
    blocks = blocks[blocks.ALAND20 > 0]

    # read headers
    geoheaders = list(pd.read_excel('2020_PLSummaryFile_FieldNames.xlsx', sheet_name=2))
    f1headers = list(pd.read_excel('2020_PLSummaryFile_FieldNames.xlsx', sheet_name=4))
    f2headers = list(pd.read_excel('2020_PLSummaryFile_FieldNames.xlsx', sheet_name=6))
    f3headers = list(pd.read_excel('2020_PLSummaryFile_FieldNames.xlsx', sheet_name=8))

    # do not need the third file, read the others
    f1 = pd.read_csv(f1path, names = f1headers, delimiter = '|')
    f2 = pd.read_csv(f2path, names = f2headers, delimiter = '|')
    geo = pd.read_csv(geopath, names = geoheaders, delimiter = '|', low_memory=False)

    # join f1 to f2
    joined = f1.merge(f2, on='LOGRECNO')

    # get columns we want
    wanted_cols = pd.read_excel('col_map.xlsx')
    cols = list(wanted_cols['Census'])
    cols.append('LOGRECNO')

    # subset to what we want
    joined = joined[cols]

    # map census names to mggg names
    mapper = {
        c: "LOGRECNO" if c == "LOGRECNO" else wanted_cols[wanted_cols['Census'] == c].iloc[0]['MGGG'] for c in cols
    }
    joined = joined.rename(mapper = mapper, axis = 1)

    # add geographic info
    with_geo = joined.merge(geo[['LOGRECNO', 'GEOCODE', 'SUMLEV', 'CD116', 'SLDU18', 'SLDL18']], on = 'LOGRECNO')
    with_geo = with_geo.drop('LOGRECNO', axis = 1)
    with_geo['GEOCODE'] = with_geo['GEOCODE'].apply(str)
    blocks['GEOID20'] = blocks['GEOID20'].apply(str)

    # add geometry  
    final = blocks.merge(with_geo, left_on='GEOID20', right_on='GEOCODE')  
    final.to_file(outfile) 

if __name__ == "__main__":
    main()