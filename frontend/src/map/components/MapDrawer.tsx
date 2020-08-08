import React, { useState, useEffect } from "react";
import { Drawer, Button, Card } from "@blueprintjs/core";
import { useAPIResult } from "./APIResult";

/* This component will Handle the drawer or whatever 
info box we decide on to display data from the MacroStrat 
API based on a click on the map */

// USE TOASTER it'll be way cooler

export function MapDrawer({ drawOpen, closeToast, clickPnt }) {
  const [macrostratData, setMacrostratData] = useState([]);

  // url to queary macrostrat
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
        hasBackdrop={false}
        canOutsideClickClose={false}
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
