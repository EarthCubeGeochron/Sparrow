import { hyperStyled } from "@macrostrat/hyper";
import { useModelEditor } from "@macrostrat/ui-components";
import { useState, useContext, useEffect } from "react";
import MapGL from "@urbica/react-map-gl";
import Draw from "@urbica/react-map-gl-draw";
import { FormSlider } from "./utils";
import { ModelEditableText } from "../project/editor";
import { ProjectFormContext } from "../project/new-project";
import { useAPIv2Result } from "~/api-v2";
import { MySuggest } from "../../components/blueprint.select";
import { FormGroup, Button, Icon, Tooltip } from "@blueprintjs/core";
import { HelpButton, MySwitch } from "~/components";
import { MyNumericInput } from "../../components/edit-sample";
import styles from "./module.styl";

const h = hyperStyled(styles);

export function NewSampleMap(props) {
  const { changeCoordinates, sample } = props;
  const { longitude = 0, latitude = 0 } = sample;

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

export const SampleLocation = (props) => {
  const { sample, changeCoordinates, stacked = true } = props;
  const { longitude, latitude } = sample;
  const [loc, setLoc] = useState({
    longitude: longitude,
    latitude: latitude,
  });

  const classname = stacked ? "sample-loc-inputs" : "sample-loc-inputs-long";

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

  return h(`div.${classname}`, [
    h(MyNumericInput, {
      label: "Latitude",
      value: loc.latitude,
      onChange: onChangeLat,
      helperText: "-90 to 90",
      placeholder: "Enter latitude",
      min: -90,
      max: 90,
    }),
    h(MyNumericInput, {
      label: "Longitude",
      value: loc.longitude,
      onChange: onChangeLon,
      helperText: "-180 to 180",
      placeholder: "Enter longitude",
      min: -180,
      max: 180,
    }),
  ]);
};

export const SampleDepth = (props) => {
  const [disabled, setDisabled] = useState(true);
  const { sample, changeDepth } = props;
  const { depth } = sample;

  useEffect(() => {
    if (disabled) {
      changeDepth(null);
    }
  }, [disabled]);

  return h("div", [
    h("div", { style: { display: "flex" } }, [
      "Depth (m): ",
      h(MySwitch, {
        checked: !disabled,
        onChange: () => setDisabled(!disabled),
      }),
    ]),
    h.if(!disabled)(MyNumericInput, {
      value: depth,
      onChange: changeDepth,
    }),
  ]);
};

const unwrapElevation = (obj) => {
  const { success } = obj;
  return success.data.elevation;
};

export const SampleElevation = (props) => {
  const [disabled, setDisabled] = useState(true);
  const { sample, changeElevation } = props;
  const { elevation, longitude, latitude } = sample;

  const elev = useAPIv2Result(
    "https://macrostrat.org/api/v2/mobile/map_query_v2",
    {
      lng: longitude || 0,
      lat: latitude || 0,
      z: 3,
    },
    {
      unwrapResponse: unwrapElevation,
    }
  );
  useEffect(() => {
    if (elev) {
      if (longitude && latitude && !disabled) {
        changeElevation(elev);
      }
    }
  }, [elev]);

  useEffect(() => {
    if (disabled) {
      changeElevation(null);
    }
  }, [disabled]);

  return h("div", [
    h(MyNumericInput, {
      label: h("div", { style: { display: "flex", alignItems: "baseline" } }, [
        "Elevation (m): ",
        h(MySwitch, {
          checked: !disabled,
          onChange: () => setDisabled(!disabled),
        }),
      ]),
      value: elevation,
      onChange: changeElevation,
      disabled,
    }),
  ]);
};

const unwrapMacroStratNames = (obj) => {
  const { success } = obj;
  const StratNames = success.data.map((ele) => ele.strat_name_long);
  return StratNames.slice(0, 20);
};

const unwrapSparrowGeoEntites = (obj) => {
  const { data } = obj;
  const entities = data.map((ele) => ele.name);
  return entities;
};

export const SampleGeoEntity = (props) => {
  const { geoEntity, changeGeoEntity } = props;
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
      label: "Geologic Entity Name",
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

export function EntityType(props) {
  const onChange = (entity) => {
    console.log(entity);
  };

  return h(FormGroup, { label: "Entity Type" }, [
    h(MySuggest, {
      items: [
        "Formation",
        "Memeber",
        "Unit",
        "Lake",
        "Glacier",
        "Volcano",
        "Ashbed",
      ],
      onChange,
    }),
  ]);
}

export function GeoSpatialRef(props) {
  const { distance, onDistanceChange } = props;
  const onChange = (ref) => {
    console.log(ref);
  };
  return h("div", [
    h(FormGroup, { label: "Spatial Reference" }, [
      h(MySuggest, { items: ["top", "bottom"], onChange }),
    ]),
    h(MyNumericInput, {
      label: "Distance from reference (m)",
      value: distance,
      onChange: onDistanceChange,
    }),
  ]);
}

/**
 * Component for placing sample in geologic context
 *  Pick GeoEntity, name of entity from macrostrat
 *  Entity Type: "formation, member, unit, glacier, lake, etc.."
 *  GeoSpatial Reference:
 *      Ref datum :"Top, Bottom",
 *      Ref Distance: Number, meters from ref datum
 *  Examples for what possible choices are....
 */
export function GeoContext(props) {
  const [distance, setDistance] = useState(null);
  const { sample, changeGeoEntity } = props;

  const helpContent = h("div.help-geo-entity", [
    h("div", [
      h("b", "Spatial Reference"),
      ": Reference point on geo-entity, from which measurement was taken.",
    ]),
    h("div", [
      h("b", "Distance from reference"),
      ": A measured distance in meters from the spatial reference point.",
    ]),
    h("div", [
      h("b", "Example"),
      ": A ",
      h("b", "Spatial Reference"),
      " of ",
      h("b", "top"),
      " and a ",
      h("b", "Distance"),
      " of ",
      h("b", "0.2"),
      " means that the sample was taken ",
      h("b", "0.2 meters"),
      " from the top of the geo entity.",
    ]),
  ]);

  const content = h("div.geo-entity-drop", [
    h("div.entity", [
      h(SampleGeoEntity, { sample, changeGeoEntity }),
      h(EntityType),
    ]),
    h(GeoSpatialRef, { distance, onDistanceChange: setDistance }),
  ]);

  return h("div", [
    "Geologic Context",
    h(HelpButton, { content: helpContent, position: "top" }),
    content,
  ]);
}

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
export const SampleMaterial = (props) => {
  const { sample, changeMaterial } = props;
  const { material } = sample;
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

  return h("div", [
    h(FormGroup, { label: h("h4", "Material"), helperText: "Lithologies" }, [
      h(MySuggest, {
        items: materials,
        onChange: changeMaterial,
        onFilter: (query) => {
          setQuery(query);
        },
      }),
    ]),
    h("h4", ["Currently: ", material ? material : "No Material"]),
  ]);
};

const PoweredByMacroSparrow = () => {
  const content = h("h5", [
    "Powered by ",
    h("a", { href: "https://macrostrat.org/" }, ["Macrostrat"]),
    " and ",
    h("a", { href: "https://macrostrat.org/" }, ["Sparrow"]),
  ]);

  return h(Tooltip, { content }, [h(Icon, { icon: "info-sign" })]);
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
function NewSampleForm({ onSubmit }) {
  const [sample, setSample] = useState({});

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
    return h(Button, { onClick: () => onSubmit(sample), intent: "success" }, [
      "Create New Sample",
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
    h(SampleMaterial, { changeMaterial, sample }),
    h("div.metadata-body", [
      h(GeoContext, { sample, changeGeoEntity }),
      h(PoweredByMacroSparrow),
    ]),
    h(SubmitButton),
  ]);
}

export function NewSampleToModel({ onSubmit }) {
  return h("div", [
    h(FormSlider, {
      content: h(NewSampleForm, { onSubmit }),
      model: "sample",
    }),
  ]);
}

export function NewProjNewSample() {
  const { dispatch } = useContext(ProjectFormContext);

  const onSubmit = (sample) => {
    dispatch({ type: "add_sample", payload: { sample_collection: [sample] } });
  };

  return h(NewSampleToModel, { onSubmit });
}

export function EditProjNewSample({ onSubmit }) {
  return h(NewSampleToModel, { onSubmit });
}
