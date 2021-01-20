import os
from dateutil import tz
from datetime import timedelta

import gpxpy
import geopy.distance


class Track:
    def __init__(self, track, distance, startTime, endTime):
        self.track = track
        self.distance = distance
        self.startTime = startTime
        self.endTime = endTime

    def duration(self):
            if self.startTime != "" and self.endTime != "":
                return self.endTime - self.startTime
            else:
                return timedelta(0)

    def durationToStr(self):
        duration = self.duration()
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


def main(gpxFilename, htmlFilename) -> None:
    track: Track = load_track(gpxFilename)
    if(track != None and len(track.track) > 0):
        generate_html(track, htmlFilename)
        print("Done generating html page: ", htmlFilename)


def load_track(filename: str) -> Track:
    if(os.path.exists(filename) == False):
        print(f"File not found: {filename}")
        return None
    localtime = tz.tzlocal()
    gpx_file = open(filename)
    current_track = Track([], 0, "", "")
    try:
        gpx = gpxpy.parse(gpx_file)
        prevPoint = (0, 0)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    current_track.track.append([float(point.latitude), float(point.longitude)])
                    if current_track.startTime == "":
                        current_track.startTime = point.time.astimezone(localtime)
                    current_track.endTime = point.time.astimezone(localtime)
                    if prevPoint != (0, 0):
                        pointDistance = geopy.distance.distance(prevPoint, (float(point.latitude), float(point.longitude))).km
                        current_track.distance = current_track.distance + pointDistance
                    prevPoint = (float(point.latitude),float(point.longitude))
    except Exception as error:
        print(f"\nParsing file '{filename}' failed. Error: {error}")
        current_track = None
    gpx_file.close()
    return(current_track)


def generate_html(track: Track, file_out: str) -> None:
    """Generates a new html file with points"""
    template = """
    <html><head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A==" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js" integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA==" crossorigin=""></script>
  <style type="text/css">
  #mapId {
    position: absolute;
    top: 0px;
    width: 800px;
    left: 0px; 
    height: 800px;
    border: 1px solid #000;
  }  
  #info {
    position: absolute;
    top: 0px;
    left: 805px;
    border: 1px solid #000;
    background-color: #ddd;
    font-size: larger;
    padding: 5px;
  }
</style>
</head>
<body>
  <div id="mapId"></div>
  <div id="info">
    <h1>Track info</h1>
    <div id="duration"></div>
    <div id="distance"></div>
  </div>
  <script>
    var myMap = L.map('mapId').setView([55.641, 12.47], 13);
    L.tileLayer(
      'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
          '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
          'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        id: 'mapbox/streets-v11',
        tileSize: 512,
        zoomOffset: -1
      }).addTo(myMap);
    var track = [];
    var duration = '';
    var distance = '';
    L.polyline(track, {color: 'blue'}).addTo(myMap);;
  </script>
</body></html>    
    """

    track_points = ",".join([f"[{g_track_point[0]}, {g_track_point[1]}, 0.1]" for g_track_point in track.track])
    track_points = f"var track=[{track_points}];"
    template = template.replace("var track = [];", track_points)
    template = template.replace('<div id="duration"></div>', '<div id="duration">Duration: ' + track.durationToStr() + '</div>')
    template = template.replace('<div id="distance"></div>', '<div id="distance">Distance: ' + str(round(track.distance, 2)) + ' km</div>')
    f = open(file_out, "w")
    f.write(template)
    f.close()


if __name__ == '__main__':
    main("myTrack.gpx", "myTrack.html")
