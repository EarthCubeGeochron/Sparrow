import { hyperStyled } from "@macrostrat/hyper";
import { useState, useContext, useEffect } from "react";
import MapGL from "@urbica/react-map-gl";
import Draw from "@urbica/react-map-gl-draw";
import { FormSlider } from "./utils";
import { ModelEditableText } from "../project/editor";
import { ProjectFormContext } from "../project/new-project";
import { useAPIv2Result } from "~/api-v2";
import { MySuggest } from "../../components/blueprint.select";
import { FormGroup, Button, Icon, Tooltip } from "@blueprintjs/core";
import { MyNumericInput } from "../../components/edit-sample";
import styles from "./module.styl";

const h = hyperStyled(styles);

function NewSampleMap(props) {
  const { changeCoordinates, sample } = props;
  const { longitude, latitude } = sample;

  const [point, setPoint] = useState({
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        properties: {},
        geometry: {
          coordinates: [longitude, latitude],
          type: "Point",
        },
      },
    ],
  });

  const handleChange = (data) => {
    const { features } = data;
    const { geometry } = features.slice(-1)[0];
    setPoint((prevPoint) => {
      return {
        ...prevPoint,
        features: features.slice(-1),
      };
    });
    const { coordinates } = geometry;
    const [lon, lat] = coordinates;
    const long = Number(lon).toFixed(3);
    const lati = Number(lat).toFixed(3);
    changeCoordinates({ lon: long, lat: lati });
  };

  return h(
    MapGL,
    {
      className: "map",
      style: { width: "100%", height: "300px" },
      mapStyle: "mapbox://styles/mapbox/light-v9",
      accessToken: process.env.MAPBOX_API_TOKEN,
      latitude: 0,
      longitude: 0,
      zoom: 0,
    },
    [
      h(Draw, {
        data: point,
        onChange: handleChange,
        polygonControl: false,
        lineStringControl: false,
        uncombineFeaturesControl: false,
        combineFeaturesControl: false,
      }),
    ]
  );
}

const SampleLocation = (props) => {
  const { sample, changeCoordinates } = props;
  const { longitude, latitude } = sample;
  const [loc, setLoc] = useState({
    longitude: longitude,
    latitude: latitude,
  });

  useEffect(() => {
    setLoc({
      longitude,
      latitude,
    });
  }, [longitude == loc.longitude]);

  const onChangeLat = (value) => {
    setLoc((prevLoc) => {
      return {
        ...prevLoc,
        latitude: value,
      };
    });
    changeCoordinates({ lon: loc.longitude, lat: value });
  };
  const onChangeLon = (value) => {
    let lon = value;
    setLoc((prevLoc) => {
      return {
        ...prevLoc,
        longitude: lon,
      };
    });
    changeCoordinates({ lon: value, lat: loc.latitude });
  };

  return h("div.sample-loc-inputs", [
    h(MyNumericInput, {
      label: "Latitude",
      value: loc.latitude,
      onChange: onChangeLat,
      helperText: "between -90 and 90",
      placeholder: "Enter latitude",
      min: -90,
      max: 90,
    }),
    h(MyNumericInput, {
      label: "Longitude",
      value: loc.longitude,
      onChange: onChangeLon,
      helperText: "between -180 and 180",
      placeholder: "Enter longitude",
      min: -180,
      max: 180,
    }),
  ]);
};

const SampleDepth = (props) => {
  const { sample, changeDepth } = props;
  const { depth } = sample;

  return h(MyNumericInput, {
    label: "Depth (m)",
    value: depth,
    onChange: changeDepth,
  });
};

const unwrapElevation = (obj) => {
  const { success } = obj;
  return success.data.elevation;
};
const SampleElevation = (props) => {
  const { sample, changeElevation } = props;
  const { elevation } = sample;

  const elev = useAPIv2Result(
    "https://macrostrat.org/api/v2/mobile/map_query_v2",
    {
      lng: sample.longitude,
      lat: sample.latitude,
      z: 3,
    },
    {
      unwrapResponse: unwrapElevation,
    }
  );
  useEffect(() => {
    if (elev) {
      changeElevation(elev);
    }
  }, [elev]);

  return h(MyNumericInput, {
    label: "Elevation (m)",
    value: elevation,
    onChange: changeElevation,
  });
};

const unwrapMacroStratNames = (obj) => {
  const { success } = obj;
  const StratNames = success.data.map((ele) => ele.strat_name);
  return StratNames.slice(0, 20);
};

const unwrapSparrowGeoEntites = (obj) => {
  const { data } = obj;
  const entities = data.map((ele) => ele.name);
  return entities;
};

const SampleGeoEntity = (props) => {
  const { sample, changeGeoEntity } = props;
  const [query, setQuery] = useState("");
  const [entities, setEntities] = useState([]);

  const macroStratNames = useAPIv2Result(
    "https://macrostrat.org/api/v2/defs/strat_names",
    { strat_name_like: query },
    { unwrapResponse: unwrapMacroStratNames }
  );

  const sparrowEntities = useAPIv2Result(
    "/models/geo_entity",
    {
      like: query,
      per_page: 20,
    },
    { unwrapResponse: unwrapSparrowGeoEntites }
  );

  useEffect(() => {
    if (macroStratNames) {
      if (sparrowEntities) {
        const entityNames = new Set([...macroStratNames, ...sparrowEntities]);
        setEntities([...entityNames]);
      }
    }
  }, [macroStratNames]);

  return h(
    FormGroup,
    {
      label: "Geologic Entity",
      helperText: "Formation, member, unit, etc...",
    },
    [
      h(MySuggest, {
        items: entities,
        onChange: changeGeoEntity,
        onFilter: (query) => setQuery(query),
      }),
    ]
  );
};

const unwrapMaterialDataSp = (obj) => {
  const { data } = obj;
  const materials = data.map((ele) => ele.id);
  return materials;
};
const unwrapMacroMaterials = (obj) => {
  const { success } = obj;
  const materials = success.data.map((ele) => ele.name);
  return materials;
};
/**
 * Will use materials from sparrow and macrostrat
 *
 */
const SampleMaterial = (props) => {
  const { sample, changeMaterial } = props;
  const [query, setQuery] = useState("");
  const initMaterials = useAPIv2Result(
    "/vocabulary/material",
    {
      like: query,
    },
    { unwrapResponse: unwrapMaterialDataSp }
  );
  const macrostratMat = useAPIv2Result(
    "https://macrostrat.org/api/v2/defs/lithologies",
    { all: true },
    { unwrapResponse: unwrapMacroMaterials }
  );
  const [materials, setMaterials] = useState([]);

  useEffect(() => {
    if (initMaterials) {
      if (macrostratMat) {
        const mySet = new Set([...initMaterials, ...macrostratMat]);
        setMaterials([...mySet]);
      }
    }
  }, [initMaterials, macrostratMat]);

  const content = h("h5", [
    "Powered by ",
    h("a", { href: "https://macrostrat.org/" }, ["Macrostrat"]),
    " and ",
    h("a", { href: "https://macrostrat.org/" }, ["Sparrow"]),
  ]);

  return h("div", [
    h(FormGroup, { label: "Material" }, [
      h(MySuggest, {
        items: materials,
        onChange: changeMaterial,
        onFilter: (query) => {
          setQuery(query);
        },
      }),
    ]),
    h(Tooltip, { content }, [h(Icon, { icon: "info-sign" })]),
  ]);
};

const SampleName = (props) => {
  const [name, setName] = useState("");
  const { changeName } = props;

  const onChange = (e) => {
    setName(e);
    changeName(e);
  };

  return h(ModelEditableText, {
    is: "h3",
    field: "sample",
    placeholder: "Name your sample",
    editOn: true,
    onChange,
    value: name,
    multiline: true,
  });
};

/**
 * Things Needed on a Sample Form
 * depth
 * elevation
 * embargo_date
 * igsn
 * location: lat/lng
 * material
 * name
 * projects
 * sample_geo_entity => geo formations (macrostrat)
 * session_collection
 * data_file_links?
 *
 */
function NewSampleForm(props) {
  const [sample, setSample] = useState({
    name: "",
    depth: 0,
    elevation: 0,
    latitude: 0,
    longitude: 0,
    material: "",
    sample_geo_entity: "",
  });

  const { dispatch } = useContext(ProjectFormContext);

  const onSubmit = () => {
    dispatch({ type: "add_sample", payload: { sample_collection: [sample] } });
  };

  console.log(sample);
  const changeCoordinates = (coords) => {
    const { lat, lon } = coords;

    setSample((prevSample) => {
      return {
        ...prevSample,
        latitude: lat,
        longitude: lon,
      };
    });
  };

  const changeName = (name) => {
    setSample((prevSample) => {
      return {
        ...prevSample,
        name,
      };
    });
  };

  const changeDepth = (depth) => {
    setSample((prevSample) => {
      return {
        ...prevSample,
        depth,
      };
    });
  };
  const changeElevation = (elevation) => {
    setSample((prevSample) => {
      return {
        ...prevSample,
        elevation,
      };
    });
  };
  const changeMaterial = (material) => {
    setSample((prevSample) => {
      return {
        ...prevSample,
        material,
      };
    });
  };

  const changeGeoEntity = (entity) => {
    setSample((prevSample) => {
      return {
        ...prevSample,
        sample_geo_entity: entity,
      };
    });
  };

  const SubmitButton = () => {
    return h(Button, { onClick: onSubmit, intent: "success" }, [
      "Creat New Sample",
    ]);
  };

  return h("div.drawer-body", [
    h(SampleName, { changeName }),
    h("div.location", [
      h("div", [
        h(SampleLocation, { changeCoordinates, sample }),
        h(SampleDepth, { sample, changeDepth }),
        h(SampleElevation, { sample, changeElevation }),
      ]),
      h("div.sample-map", [h(NewSampleMap, { changeCoordinates, sample })]),
    ]),
    h("div.metadata-body", [
      h(SampleMaterial, { changeMaterial, sample }),
      h(SampleGeoEntity, { sample, changeGeoEntity }),
    ]),
    h(SubmitButton),
  ]);
}

function NewSampleToModel(props) {
  return h("div", [
    h(FormSlider, {
      content: h(NewSampleForm),
      model: "sample",
    }),
  ]);
}

export { NewSampleToModel };
