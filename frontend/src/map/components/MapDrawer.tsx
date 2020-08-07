import React, { useState, useEffect } from "react";
import { Drawer, Button, Card } from "@blueprintjs/core";
import { useAPIResult } from "./APIResult";

/* This component will Handle the drawer or whatever 
info box we decide on to display data from the MacroStrat 
API based on a click on the map */

export function MapDrawer({ drawOpen, setDrawOpen, clickPnt }) {
  const [macrostratData, setMacrostratData] = useState([]);
  const MacURl = "https://macrostrat.org/api/v2/geologic_units/map";

  const MacostratData = useAPIResult(MacURl, {
    lng: clickPnt.lng,
    lat: clickPnt.lat,
  });

  useEffect(() => {
    if (MacostratData == null) return;
    setMacrostratData(MacostratData.success.data);
    console.log(macrostratData);
  }, [MacostratData]);

  return (
    <div>
      <Drawer
        isOpen={drawOpen}
        autoFocus={false}
        enforceFocus={false}
        onClose={() => setDrawOpen(false)}
      >
        {macrostratData.map((object) => {
          return (
            <div>
              <p key={object.name}>{"Name: " + object.name}</p>
              <p key={object.lith}>{"Lithology: " + object.lith}</p>
            </div>
          );
        })}
      </Drawer>
    </div>
  );
}
