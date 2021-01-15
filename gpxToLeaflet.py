import gpxpy
import os

def main(gpxFilename, htmlFilename) -> None:
    track: list = load_track(gpxFilename)
    if(track != None and len(track) > 0):
        generate_html(track, htmlFilename)
        print("Done generating html page: ", htmlFilename)

def load_track(filename: str) -> list:
    trackPoints: list = []
    if(os.path.exists(filename) == False):
        print(f"File not found: {filename}")
        return
    gpx_file = open(filename)
    try:
        gpx = gpxpy.parse(gpx_file)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    trackPoints.append(
                        [float(point.latitude), float(point.longitude)])
    except Exception as error:
        print(f"\nParsing file '{filename}' failed. Error: {error}")
    gpx_file.close()
    return(trackPoints)

def generate_html(track: list, file_out: str) -> None:
    """Generates a new html file with points"""
    template = """
    <html><head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A==" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js" integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA==" crossorigin=""></script>
  <style type="text/css">
  #mapId {
    position: absolute;
    top: 0px;
    width: 1000px;
    left: 0px; 
    height: 1000px;
    border: 1px solid #000;
  }  
</style>
</head>
<body>
  <div id="mapId"></div>
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
    L.polyline(track, {color: 'blue'}).addTo(myMap);;
  </script>
</body></html>    
    """

    track_points = ",".join([f"[{g_track_point[0]}, {g_track_point[1]}, 0.1]" for g_track_point in track])
    track_points = f"var track=[{track_points}];"
    template = template.replace("var track = [];", track_points)
    f = open(file_out, "w")
    f.write(template)
    f.close()

if __name__ == '__main__':
    main("myTrack.gpx", "myTrack.html")
