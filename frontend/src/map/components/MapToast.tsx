import * as React from "react";
import { useState, useEffect } from "react";
import {
  Button,
  Card,
  Collapse,
  Spinner,
  Divider,
  Dialog,
  NumericInput,
} from "@blueprintjs/core";
import { useAPIResult, useToggle } from "./APIResult";
import { mapStyle } from "../MapStyle";

/**
 * This component will Handle the Toast or whatever
 * info box we decide on to display data from the MacroStrat
 * API based on a click on the map. The Toast Message content
 * should be different based on which mapstyle is selected in
 * the MapPanel Component.
 *
 * Need to find an API that returns an elevation based on location
 */

export function MapToast({ lng, lat, mapstyle }) {
  const [open, toggleOpen] = useToggle(false);

  // url to queary macrostrat
  const MacURl = "https://macrostrat.org/api/v2/geologic_units/map";

  // url to queary Rockd, requires a lat and lng and returns a nearby town
  const RockdURL = "https://rockd.org/api/v2/nearby";

  const rockdNearbyData = useAPIResult(RockdURL, {
    lat: lat,
    lng: lng,
  });

  const MacostratData = useAPIResult(MacURl, {
    lng: lng,
    lat: lat,
  });
  //console.log(); // if MacrostratData.success.data.length is 0... there is no associated data.
  const NearByCity = () => {
    const [open, toggleOpen] = useToggle(false);
    return (
      <div>
        <h5>
          Nearby: <i>{rockdNearbyData}</i>
        </h5>
        <Button onClick={toggleOpen}>Add Sample at Location</Button>
        <Dialog
          isOpen={open}
          title="Add Sample At Location"
          onClose={toggleOpen}
        >
          <p>Longitude: </p>
          <NumericInput defaultValue={lng}></NumericInput>
          <p>Latitude</p>
          <NumericInput defaultValue={lat}></NumericInput>
          <p>Suggested Geologic Formations</p>
        </Dialog>
      </div>
    );
  };

  const NearbyGeologicFormations = () => {
    return (
      <div>
        {MacostratData == null ? (
          <Spinner size={50} />
        ) : MacostratData.success.data.length == 0 ? null : (
          <div>
            <h5>
              Information Provided by{" "}
              <a href="https://macrostrat.org/">MacroStrat</a>
            </h5>

            {MacostratData.success.data.map((object) => {
              return (
                <div>
                  <h4 style={{ color: "black" }}>
                    {object.name + ": "}
                    <i>{object.b_age + " Ma" + " - " + object.t_age + " Ma"}</i>
                  </h4>
                  <h5>
                    <p key={object.name}>{object.b_init_name}</p>
                    <p key={object.name}>{object.descrip}</p>
                    {/* <p key={object.lith}>{object.lith}</p> */}
                  </h5>
                  <Divider />
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };
  return (
    <div>
      <h5>
        <b>Longitude: </b>
        <i>{Number(lng).toFixed(3) + " "}</i>
        <b>Latitude: </b>
        <i>{Number(lat).toFixed(3)}</i>
      </h5>
      <Divider />
      {mapstyle == mapStyle ? <NearbyGeologicFormations /> : <NearByCity />}
    </div>
  );
}
