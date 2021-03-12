import React, { useState, useEffect } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { FormGroup, Button } from "@blueprintjs/core";
import { HelpButton } from "~/components";
import { useAPIv2Result } from "~/api-v2";
import { sample_geo_entity } from "../../sample/new-sample/types";
import { MySuggest } from "../../../components/blueprint.select";
import { MyNumericInput } from "../../../components/edit-sample";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

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
  const { onEntityTypeChange } = props;
  const onChange = (entity) => {
    console.log(entity);
    onEntityTypeChange(entity);
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
  const {
    geoEntity,
    changeDistance = () => {},
    changeDatum = () => {},
    changeUnit = () => {},
  } = props;

  const { ref_distance } = geoEntity;

  const onChange = (ref) => {
    console.log(ref);
    changeDatum(ref);
    changeUnit("meters");
  };
  return h("div", [
    h(FormGroup, { label: "Spatial Reference" }, [
      h(MySuggest, { items: ["top", "bottom"], onChange }),
    ]),
    h(MyNumericInput, {
      label: "Distance from reference (m)",
      value: ref_distance,
      onChange: changeDistance,
    }),
  ]);
}

function GeoEntityText(props) {
  const {
    sample_geo_entity,
  }: { sample_geo_entity: sample_geo_entity[] } = props;
  if (!sample_geo_entity) return null;
  console.log(sample_geo_entity);

  const listofEntityStrings = sample_geo_entity.map((sample_geo_entity) => {
    const { geo_entity, ref_datum, ref_distance, ref_unit } = sample_geo_entity;
    const { type, name } = geo_entity;

    const geoEntityString = `This sample is from the ${name} ${type}. `;
    const refString = `This sample was taken ${ref_distance} ${ref_unit} from the ${ref_datum} of the geo_entity.`;

    const fullString =
      name && ref_distance
        ? geoEntityString + refString
        : name
        ? geoEntityString
        : null;

    return fullString;
  });
  return h("div", [listofEntityStrings.map((string) => string)]);
}

function GeoEntityTextContainer(props) {
  const {
    geoEntityText,
    geoEntity,
    onClick,
  }: {
    geoEntityText: string;
    geoEntity: sample_geo_entity;
    onClick: (entity) => void;
  } = props;

  return h("div.entity-edit-card", [
    h("h4", [geoEntityText]),
    h(
      Button,
      h(Button, {
        minimal: true,
        icon: "trash",
        intent: "danger",
        onClick: () => onClick(geoEntity),
      })
    ),
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
 * TODO: Have output section, editable like other collections, reads it human like
 */
export function GeoContext(props) {
  const {
    sample_geo_entity,
    changeGeoEntity,
  }: {
    sample_geo_entity: sample_geo_entity[];
    changeGeoEntity: (g) => void;
  } = props;
  const defaultState: sample_geo_entity = {
    ref_datum: null,
    ref_distance: null,
    ref_unit: null,
    geo_entity: { type: null, name: null },
  };
  const [geoEntity, setGeoEntity] = useState<sample_geo_entity>(defaultState);
  console.log(geoEntity);

  const changeDatum = (datum: string) => {
    setGeoEntity((prevEntity) => {
      return {
        ...prevEntity,
        ref_datum: datum,
      };
    });
  };

  const changeDistance = (distance: number) => {
    setGeoEntity((prevEntity) => {
      return {
        ...prevEntity,
        ref_distance: distance,
      };
    });
  };

  const changeUnit = (unit: string) => {
    setGeoEntity((prevEntity) => {
      return {
        ...prevEntity,
        ref_unit: unit,
      };
    });
  };
  const changeGeoType = (type: string) => {
    setGeoEntity((prevEntity) => {
      const { name } = prevEntity.geo_entity;
      return {
        ...prevEntity,
        geo_entity: { type, name },
      };
    });
  };
  const changeGeoName = (name: string) => {
    setGeoEntity((prevEntity) => {
      const { type } = prevEntity.geo_entity;
      return {
        ...prevEntity,
        geo_entity: { name, type },
      };
    });
  };

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

  const onSubmitClick = () => {
    changeGeoEntity(geoEntity);
    setGeoEntity(defaultState);
  };

  const { geo_entity } = geoEntity;
  const { type, name } = geo_entity;

  const content = h("div.geo-entity-drop", [
    h("div.entity", [
      h(SampleGeoEntity, { name, changeGeoEntity: changeGeoName }),
      h(EntityType, { type, onEntityTypeChange: changeGeoType }),
    ]),
    h(GeoSpatialRef, { geoEntity, changeDistance, changeDatum, changeUnit }),
    h(Button, { intent: "success", onClick: onSubmitClick }, ["Submit"]),
  ]);

  return h("div", [
    "Geologic Context",
    h(HelpButton, { content: helpContent, position: "top" }),
    content,
    h(GeoEntityText, { sample_geo_entity }),
  ]);
}
