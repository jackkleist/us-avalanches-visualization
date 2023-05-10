# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import folium
import pandas as pd
from enum import Enum
import webbrowser
import requests


class Color(Enum):
    red = 'Climber'
    purple = 'Mechanized Guide'
    lightgreen = 'Backcountry Tourer'
    black = 'Snowmobiler'
    pink = 'Resident'
    lightblue = 'Hiker'
    cadetblue = 'Hybrid Rider'
    green = 'Sidecountry Rider'
    darkpurple = 'Inbounds Rider'


class AvyDf(pd.DataFrame):
        @property
        def _constructor(self):
            return AvyDf

        def clean(self):
            self.dropna(inplace=True)
            self.set_index('Date')
            self['lat'] = pd.to_numeric(self['lat'])
            self['lon'] = pd.to_numeric(self['lon'])
            self['Killed'] = pd.to_numeric(self['Killed'])
            self.replace(to_replace='Mechanised Guide', value='Mechanized Guide',inplace=True)

class Map:
    def __init__(self, center, zoom_start):
        self.center = center
        self.zoom_start = zoom_start
        self.tile_set = 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}'
        self.attr = 'Tiles courtesy of the <a href="https://usgs.gov/">U.S. Geological Survey</a>'
        self.high_bound = [71.746432,-49.394531]
        self.low_bound = [23.322080,-171.298828]

    def show_map(self):
        # Create the map
        map_topo = folium.Map(location=self.center, zoom_start=self.zoom_start, tiles=None, max_bounds=True)
        folium.raster_layers.TileLayer(tiles=self.tile_set, name='USGS Topographic', attr=self.attr,
                                       min_zoom=self.zoom_start, control=False).add_to(map_topo)
        # this adds a topo map layer to the legend
        lgd_txt = '<span style="color: {col};">{txt}</span>'
        popup_txt = '<h4>{loc}</h4><p>{date}</p><p>{des}</p>'
        for color in Color:
            color_str = color.name
            fg = folium.FeatureGroup(name=lgd_txt.format(txt=color.value, col=color_str))
            for index, row in avy_df.iterrows():
                activity_color = Color(row['PrimaryActivity']).name
                if activity_color == color_str:
                    fm = folium.Marker(
                        location=[row['lat'], row['lon']],
                        icon=folium.Icon(color=activity_color, prefix='fa', icon='{}'.format(row['Killed'])),
                        # this line creates an icon and imports it from font awesome.com
                        tooltip=popup_txt.format(date=row.name, loc=row['Location'], des=row['Description'])
                    )
                    fg.add_child(fm)
            map_topo.add_child(fg)
        folium.features.ClickForLatLng().add_to(map_topo)
        folium.map.FitBounds((self.low_bound, self.high_bound)).add_to(map_topo)
        folium.map.LayerControl('topleft', collapsed=False, sortLayers=True).add_to(map_topo)
        # Display the map
        map_topo.save("map.html")
        webbrowser.open("map.html")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    url = 'https://avalanche.state.co.us/sites/default/files/2022-11/Accidents_2022_PUBLIC.xlsx'
    r = requests.get(url, allow_redirects=True)
    open('avalanche_accidents.xlsx', 'wb').write(r.content)
    avy_df = AvyDf(pd.read_excel('avalanche_accidents.xlsx'))
    avy_df.clean()
    avg_lat = avy_df.loc[:, 'lat'].mean(axis=0)
    avg_lon = avy_df.loc[:, 'lon'].mean(axis=0)
    ava_map = Map([avg_lat, avg_lon], 4)
    ava_map.show_map()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
