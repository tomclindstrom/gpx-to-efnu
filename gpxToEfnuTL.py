import os
from dateutil import tz
from datetime import timedelta

import gpxpy
import geopy.distance


class DistanceMarker:
    def __init__(self, latitude, longitude, label):
        self.latitude = latitude
        self.longitude = longitude
        self.label = label

    def toJsString(self):
        return f"""
            L.marker([{self.latitude},{self.longitude}], {{
              icon: L.divIcon({{ html: '<span style="font-size: 20px; font-weight: bold">{self.label}</span>' }})
            }}).addTo(myMap);"""


class Track:
    def __init__(self, track, distance, startTime, endTime, distanceMarkers=[]):
        self.track = track
        self.distance = distance
        self.startTime = startTime
        self.endTime = endTime
        self.distanceMarkers = distanceMarkers

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

    def distanceMarkersToJsStr(self):
        return "\n".join(map(lambda marker: marker.toJsString(), self.distanceMarkers))


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
        prevDistance = 0
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
                    if(int(current_track.distance) > prevDistance):
                        prevDistance = int(current_track.distance)
                        newDistanceMarker = DistanceMarker(point.latitude, point.longitude, f"{int(prevDistance)}km")
                        current_track.distanceMarkers.append(newDistanceMarker)
                    prevPoint = (float(point.latitude), float(point.longitude))
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
    border: 1px solid red;
    background-color: #0088FF;
    font-size: larger;
    
    padding: 5px;
  }

  .efnu {
    position: absolute;
    top: 0px;
    left: 805px;
  background-color: #0088FF;
  border: 5px solid red;
  padding: 5px;

  }

  .info_efnu {
    
    color: #ffffff;
    font-size: larger;
  }
  #duration {

    color: #00FF01;
  }

  #distance {

    color: #00FF01; 
  }
  .yrno{
    top: 0px;
    display: flex;

    align-items: right;
    position: absolute;    
  }
  .latukunto{
    font-size: larger;
    color: white;

  }

  .inputR {
  height: 30px;
  width: 30px;
  appearance: none;
  background-color: red;
  border-radius: 50%;
  opacity: 1;
  align-item: center;
}
input:hover {
  cursor: pointer;
}
.tri-state-toggle {
    
  justify-content: center;
  border: 3px solid black;
  border-radius: 50px;
  width: 150px;
   font-family: system-ui, sans-serif;
  font-size: 2rem;
  font-weight: bold;
  line-height: 1.1;
  display: grid;
  grid-template-columns: 1em auto;
  gap: 0.5em;
}
#one {
  opacity: 0;
}
</style>
</head>
<body>
  <div id="mapId"></div>
  <div id="info">
  <div class=".efnu">
    <h1 class="info_efnu">Efnu Track info by Tomosart</h1>
    <div id="duration"></div>
    <div id="distance"></div>
    <br>
    <div class="latukunto">
      <input type="checkbox" id="1" class="box">Latukunto Pertsa </input><br>
      <input type="checkbox" id="2" class="box">Latukunto Vapaa tyyli</input><br>
      <input type="checkbox" id="3" class="box">Pururata OK</input><br>
      <input type="checkbox" id="4" class="box">Lentokenttä OK</input><br>
      <span>Latukunto valitse väri</span>
      <br>
      <input type="color" id="colorID" oninput="changeColor()">
    </div>
    <br>
    <!-- later div class="tri-state-toggle">
      <input class="button" type="radio" name="toggle" id="one" />
      <input class="button" type="radio" name="toggle" id="two" />
      <input class="button" type="radio" name="toggle" id="three" />
    </div -->
    <br>

    <div class="weatherWidget" ></div>
    <br>
    <div>
    <iframe src="https://www.meteoblue.com/en/weather/widget/daily/nummela_finland_11711396?geoloc=fixed&days=7&tempunit=CELSIUS&windunit=KILOMETER_PER_HOUR&precipunit=MILLIMETER&coloured=coloured&pictoicon=0&pictoicon=1&maxtemperature=0&maxtemperature=1&mintemperature=0&mintemperature=1&windspeed=0&windspeed=1&windgust=0&winddirection=0&winddirection=1&uv=0&humidity=0&humidity=1&precipitation=0&precipitation=1&precipitationprobability=0&precipitationprobability=1&spot=0&spot=1&pressure=0&pressure=1&layout=dark"  frameborder="0" scrolling="NO" allowtransparency="true" sandbox="allow-same-origin allow-scripts allow-popups allow-popups-to-escape-sandbox" style="width: 378px; height: 420px"></iframe><div><!-- DO NOT REMOVE THIS LINK --><a href="https://www.meteoblue.com/en/weather/week/nummela_finland_11711396?utm_source=weather_widget&utm_medium=linkus&utm_content=daily&utm_campaign=Weather%2BWidget" target="_blank" rel="noopener">meteoblue</a></div>
    
    
    </div>
  

    </div>
  </div>

  

  <!-- Todo radio color button -->
  <script>
  let boxes = document.getElementsByClassName('box').length;

function save() {	
  for(let i = 1; i <= boxes; i++){
	  var checkbox = document.getElementById(String(i));
    localStorage.setItem("checkbox" + String(i), checkbox.checked);	
  }
}

//for loading
for(let i = 1; i <= boxes; i++){
  if(localStorage.length > 0){
    var checked = JSON.parse(localStorage.getItem("checkbox" + String(i)));
    document.getElementById(String(i)).checked = checked;
  }
}
window.addEventListener('change', save);

  </script>

  <script>
   window.weatherWidgetConfig =  window.weatherWidgetConfig || [];
   window.weatherWidgetConfig.push({
       selector:".weatherWidget",
       apiKey:"6RXW7H4AXXLV8899EVUZSKSVV", //Sign up for your personal key
       location:"Finland, Nummela", //Enter an address
       unitGroup:"metric", //"fi" or "metric"
       forecastDays:15, //how many days forecast to show
       title:"Finland,Nummela/Efnu", //optional title to show in the 
       showTitle:true, 
       showConditions:true
   });
  
   (function() {
   var d = document, s = d.createElement('script');
   s.src = 'https://www.visualcrossing.com/widgets/forecast-simple/weather-forecast-widget-simple.js';
   s.setAttribute('data-timestamp', +new Date());
   (d.head || d.body).appendChild(s);
   })();
</script>

  <script>
    var myMap = L.map('mapId').setView([60.333889, 24.296389], 14);
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
        const polyline = L.polyline(track, {color: 'red'}).addTo(myMap);
    var highlightMarker = undefined;
    polyline.on('click', function(e) {
      const closestIdx = findPointIdxOnPolyline(track, e.latlng);
      const trackLength = lengthOfTrack(track, closestIdx);
      if(highlightMarker != undefined) {
        myMap.removeLayer(highlightMarker);
      }
      highlightMarker = L.marker(track[closestIdx], {icon: L.divIcon({ html: '<span style="font-size: 20px; font-weight: bold">' + Math.round(trackLength) + 'm</span>' })}).addTo(myMap);
    });

    function findPointIdxOnPolyline(track, latlng) {
      let prevDiffLat = prevDiffLng = 99999;
      let closestIdx = 0;
      for(var i = 0; i < track.length; i++) {
        var diffLat =  Math.abs(track[i][0] - latlng.lat);
        var diffLng = Math.abs(track[i][1] - latlng.lng);
        if(diffLat + diffLng < prevDiffLat + prevDiffLng) {
          prevDiffLat = diffLat;
          prevDiffLng = diffLng;
          closestIdx = i;
        }
      }
      return closestIdx;
    }
    function lengthOfTrack(track, idx) {
      var length = 0;
      for(var i = 1; i < track.length && i < idx; i++) {
        let from = L.latLng(track[i-1]);
        let to = L.latLng(track[i]);
        length += from.distanceTo(to);
      }
      return length;
    }
    <!--DISTANCEMARKERS-->
  </script>

  <script>
  var buttons = document.getElementsByClassName("button");
var arr = [...buttons];

arr.forEach((element, index) => {
  element.addEventListener("click", () => {
    element.style.opacity = "1";
    if (index == 0) {
      document.getElementsByTagName("body")[0].style.backgroundColor = "orange";
    } else if (index == 1) {
      document.getElementsByTagName("body")[0].style.backgroundColor = "#00FF01";
    } else {
      document.getElementsByTagName("body")[0].style.backgroundColor =  "#56B2E8";
    }
    arr
      .filter(function (item) {
        return item != element;
      })
      .forEach((item) => {
        item.style.opacity = "0";
      });
  });
});

  </script>

  <script>
  // on input, get value and save it as 'storedValue'
function changeColor() { 
  var userColor = document.getElementById('colorID').value;
  localStorage.setItem('storedValue', document.body.style.backgroundColor = userColor);
}

// if there is a value stored, update color picker and background color
if(localStorage.storedValue) {
  document.getElementById('colorID').value = localStorage.storedValue;
  document.body.style.backgroundColor      = localStorage.storedValue;
}


  </script>
</body></html>    
    """

    track_points = ",".join([f"[{g_track_point[0]}, {g_track_point[1]}, 0.1]" for g_track_point in track.track])
    track_points = f"var track=[{track_points}];"
    template = template.replace("var track = [];", track_points)
    template = template.replace('<div id="duration"></div>', '<div id="duration">Duration: ' + track.durationToStr() + '</div>')
    template = template.replace('<div id="distance"></div>', '<div id="distance">Distance: ' + str(round(track.distance, 2)) + ' km</div>')
    template = template.replace('<!--DISTANCEMARKERS-->', track.distanceMarkersToJsStr())
    f = open(file_out, "w")
    f.write(template)
    f.close()


if __name__ == '__main__':
    main("02012023TL.gpx", "EfnuTrackTL.html")
