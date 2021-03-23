import * as React from "react";
import { useState } from "react";
import {
  Button,
  Card,
  Spinner,
  Divider,
  Dialog,
  NumericInput,
  InputGroup,
} from "@blueprintjs/core";
import { useAPIResult } from "@macrostrat/ui-components";
import { useToggle } from "~/components";
import { mapStyle } from "../MapStyle";
import { MultipleSelectFilter } from "~/components";

/**
 * Form that pops up from the Toaster component.
 * Has the ability to suggest Geologic Formations from macrostrat
 */
function AddSampleAtLocal({ lng, lat, data, open, toggleOpen }) {
  const [state, setState] = useState("");

  return (
    <div style={{ position: "absolute", zIndex: 50 }}>
      <div>
        <Dialog
          isOpen={open}
          title="Add Sample At Location"
          onClose={toggleOpen}
        >
          <Card>
            <MultipleSelectFilter
              text="Connect to Sample without location: "
              items={[
                "84C207AB",
                "90T112B",
                "SMUB-13",
                "86C471B",
                "AT80-36",
                "CH9-11",
                "AT11",
                "GR-11-103",
                "NI-010813-7",
              ]}
              sendQuery={() => null}
            />
            <br></br>

            <p>Longitude: </p>
            <NumericInput defaultValue={Number(lng).toFixed(5)}></NumericInput>
            <br></br>
            <p>Latitude</p>
            <NumericInput defaultValue={Number(lat).toFixed(5)}></NumericInput>
            <br></br>

            <p>Geologic Formation: </p>
            <InputGroup
              value={state}
              onChange={(event) => setState(event.target.value)}
            />
            <h5>
              <i>Nearby units suggested by MacroStrat: </i>
            </h5>
            {data !== null ? (
              data.success.data.map((object) => {
                return (
                  <div key={object.name}>
                    <Button
                      minimal={true}
                      onClick={() => setState(object.name)}
                    >
                      {object.name}
                    </Button>
                  </div>
                );
              })
            ) : (
              <Spinner size={50} />
            )}
          </Card>
        </Dialog>
      </div>
    </div>
  );
}

/**
 * This component will Handle the Toast or whatever
 * info box we decide on to display data from the MacroStrat
 * API based on a click on the map. The Toast Message content
 * should be different based on which mapstyle is selected in
 * the MapPanel Component.
 *
 *
 */

export function MapToast({ lng, lat, mapstyle }) {
  const [open, toggleOpen] = useToggle(false);

  // url to queary macrostrat
  const MacURl = "https://macrostrat.org/api/v2/geologic_units/map";

  // url to queary Rockd, requires a lat and lng and returns a nearby town
  const RockdURL = "https://rockd.org/api/v2/nearby";

  // url to query MacroStrat to return an elevation
  const ElevationURl = `https://macrostrat.org/api/v2/mobile/map_query_v2?lng=${lng}&lat=${lat}&z=3`;

  const elevationData = useAPIResult(ElevationURl);

  const rockdNearbyData = useAPIResult(RockdURL, {
    lat: lat,
    lng: lng,
  });

  const MacostratData = useAPIResult(MacURl, {
    lng: lng,
    lat: lat,
  });

  const NearByCity = () => {
    return (
      <div>
        <h5>
          Nearby: <i>{rockdNearbyData}</i>
        </h5>
        <Divider />
      </div>
    );
  };

  const ElevationToaster = () => {
    return (
      <div>
        <h5>
          Nearby: <i>{rockdNearbyData}</i>
        </h5>
        {elevationData == null ? (
          <Spinner size={50} />
        ) : (
          <h5>
            Elevation: <i>{elevationData.success.data.elevation} meters</i>
          </h5>
        )}

        <Divider />
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
      <div style={{ position: "relative", zIndex: 0 }}>
        <div>
          <h5>
            <b>Longitude: </b>
            <i>{Number(lng).toFixed(3) + " "}</i>
            <b>Latitude: </b>
            <i>{Number(lat).toFixed(3)}</i>
          </h5>
          <Divider />
          {mapstyle == mapStyle ? (
            <NearbyGeologicFormations />
          ) : mapstyle ==
            "mapbox://styles/jczaplewski/cjftzyqhh8o5l2rqu4k68soub" ? (
            <ElevationToaster />
          ) : (
            <NearByCity />
          )}
        </div>
        <Button minimal={true} onClick={toggleOpen}>
          Add Sample at Location
        </Button>
      </div>

      <div>
        <AddSampleAtLocal
          lng={lng}
          lat={lat}
          data={MacostratData}
          open={open}
          toggleOpen={toggleOpen}
        />
      </div>
    </div>
  );
}
