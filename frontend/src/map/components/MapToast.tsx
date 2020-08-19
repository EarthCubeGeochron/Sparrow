import * as React from "react";
import { useState, useEffect } from "react";
import { Button, Card, Collapse, Spinner, Divider } from "@blueprintjs/core";
import { useAPIResult, useToggle } from "./APIResult";

/* This component will Handle the drawer or whatever 
info box we decide on to display data from the MacroStrat 
API based on a click on the map */

// USE TOASTER it'll be way cooler

export function MapToast({ lng, lat }) {
  const [open, toggleOpen] = useToggle(false);

  // url to queary macrostrat
  const MacURl = "https://macrostrat.org/api/v2/geologic_units/map";

  const MacostratData = useAPIResult(MacURl, {
    lng: lng,
    lat: lat,
  });
  console.log(MacostratData); // if MacrostratData.success.data.length is 0... there is no associated data.
  return (
    <div>
      <h5>
        <b>Longitude: </b>
        <i>{Number(lng).toFixed(3) + " "}</i>
        <b>Latitude: </b>
        <i>{Number(lat).toFixed(3)}</i>
      </h5>
      <Divider />
      <div>
        <h5>
          Information Provided by{" "}
          <a href="https://macrostrat.org/">MacroStrat</a>
        </h5>
      </div>
      {MacostratData == null ? (
        <Spinner size={50} />
      ) : MacostratData.success.data.length == 0 ? (
        <h4>No Data at this point. Click Somewhere Else</h4>
      ) : (
        MacostratData.success.data.map((object) => {
          return (
            <Card elevation={1} interactive={true} onClick={toggleOpen}>
              <h3 style={{ color: "gray" }}>
                {object.name +
                  ": " +
                  object.b_age +
                  " Ma" +
                  " to " +
                  object.t_age +
                  " Ma"}
              </h3>
              <Collapse isOpen={open}>
                <p key={object.name}>{object.b_init_name}</p>
                <p key={object.name}>{object.descrip}</p>
                <p key={object.lith}>{object.lith}</p>
              </Collapse>
            </Card>
          );
        })
      )}
    </div>
  );
}
