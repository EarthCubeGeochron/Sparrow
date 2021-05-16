import * as React from "react";
import { useState, useContext } from "react";
import {
  Button,
  Card,
  Spinner,
  Divider,
  Dialog,
  NumericInput,
  FormGroup,
  InputGroup
} from "@blueprintjs/core";
import { useAPIResult, APIHelpers } from "@macrostrat/ui-components";
import { useAPIv2Result, APIV2Context } from "~/api-v2";
import { useToggle, MySuggest } from "~/components";
import { GeoContext } from "~/model-views/components";
import { mapStyle } from "../MapStyle";
import axios from "axios";

const unwrapSamples = obj => {
  const { data } = obj;
  const names = data.map(sample => {
    const { name, id, sample_geo_entity } = sample;
    return { name, id, sample_geo_entity };
  });
  return names;
};
//needs more complex state management
function AddSampleAtLocal({ lng, lat, data, open, toggleOpen }) {
  const [state, setState] = useState("");
  const [sampleState, setSampleState] = useState({
    name: "",
    id: null,
    sample_geo_entity: []
  });
  const { buildURL } = APIHelpers(useContext(APIV2Context));

  const samples = useAPIv2Result(
    "/models/sample",
    { all: "true", not_has: "location" },
    { unwrapResponse: unwrapSamples }
  );

  const onChange = sampleName => {
    if (samples) {
      console.log(sampleName);
      const sample = samples.filter(samp => samp.name == sampleName);
      console.log(sample);
      setSampleState(sample[0]);
    }
  };

  const setGeoEntity = en => {
    // copy this from new-sample
    console.log(en);
    let SGE = [...sampleState.sample_geo_entity, ...new Array(en)];
    setSampleState(prevState => {
      return {
        ...prevState,
        sample_geo_entity: SGE
      };
    });
  };

  const onCloseDialog = () => {
    setState("");
    setSampleState({
      name: "",
      id: null,
      sample_geo_entity: []
    });
    toggleOpen();
  };

  const onSubmit = async () => {
    let url = buildURL(`/models/sample/${sampleState.id}`);
    console.log(url);
    const updatedSample = {
      ...sampleState,
      location: {
        type: "Point",
        coordinates: [Number(lng).toFixed(3), Number(lat).toFixed(3)]
      }
    };
    console.log(updatedSample);
    const response = await axios.put(url, updatedSample);
  };

  let sampleNames = [];
  if (samples) {
    sampleNames = samples.map(sample => sample.name);
  }
  if (!samples) return null;
  return (
    <div style={{ position: "absolute", zIndex: 50 }}>
      <div>
        <Dialog
          isOpen={open}
          title="Add Sample At Location"
          onClose={onCloseDialog}
        >
          <Card>
            <FormGroup label="Connect to Sample without location">
              <MySuggest
                items={sampleNames}
                onChange={onChange}
                createNew={false}
              />
            </FormGroup>
            <br></br>
            <p>Longitude: </p>
            <NumericInput defaultValue={Number(lng).toFixed(5)}></NumericInput>
            <br></br>
            <p>Latitude</p>
            <NumericInput defaultValue={Number(lat).toFixed(5)}></NumericInput>
            <br></br>
            <div>
              <GeoContext
                sample_geo_entity={sampleState.sample_geo_entity}
                changeGeoEntity={setGeoEntity}
                initialQuery={state}
              />
              <h5>
                <i>Nearby units suggested by MacroStrat: </i>
              </h5>
              {data !== null ? (
                data.success.data.map(object => {
                  return (
                    <div key={object.name}>
                      <Button
                        minimal={true}
                        onClick={() => {
                          setState(object.name);
                        }}
                      >
                        {object.name}
                      </Button>
                    </div>
                  );
                })
              ) : (
                <Spinner size={50} />
              )}
            </div>
            <Button onClick={onSubmit} intent="success">
              Submit
            </Button>
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
    lng: lng
  });

  const MacostratData = useAPIResult(MacURl, {
    lng: lng,
    lat: lat
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

            {MacostratData.success.data.map(object => {
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
