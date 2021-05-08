import { SETTINGS } from "./Settings";
import { Map, TileLayer, Popup, Marker, withLeaflet } from "react-leaflet";

export const mapStyle2 = {
  // sources:{
  //   tiles:['https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}'],
  //   attribution: 'Tiles &copy; Esri &mdash; Source: USGS, Esri, TANA, DeLorme, and NPS',
	//   maxZoom: 13
  // }
  const position = [0,0]

  render(
    <MapContainer center={position} zoom={13} scrollWheelZoom={false}>
      <TileLayer
        attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
    </MapContainer>
  )
};
