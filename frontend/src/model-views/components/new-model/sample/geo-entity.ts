import React, { useState, useEffect } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { FormGroup, Button } from "@blueprintjs/core";
import { HelpButton } from "~/components";
import { useAPIv2Result } from "~/api-v2";
import { sample_geo_entity } from "../../../sample/new-sample/types";
import { MySuggest } from "../../../../components/blueprint.select";
import { MyNumericInput } from "../../../../components/edit-sample";
import {
  ModelAttributeOneLiner,
  PageViewBlock,
  ModelLinkCard,
} from "~/model-views";
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
  const { geoEntity, changeGeoEntity, initialQuery } = props;
  const [query, setQuery] = useState("");
  const [entities, setEntities] = useState([]);

  console.log(initialQuery);
  console.log(query);
  useEffect(() => {
    if (initialQuery) {
      setQuery(initialQuery);
    }
  }, [initialQuery]);

  const changeQueryOnFilter = (query) => {
    setQuery(query);
  };

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
  }, [macroStratNames, sparrowEntities]);

  return h(
    FormGroup,
    {
      label: "Geologic Entity Name",
    },
    [
      h(MySuggest, {
        items: entities,
        initialQuery,
        onChange: changeGeoEntity,
        onFilter: changeQueryOnFilter,
      }),
    ]
  );
};

const unwrapEntityTypes = (obj) => {
  const { data } = obj;
  const types = data.map((entity) => entity.id);
  return types;
};

export function EntityType(props) {
  const { onEntityTypeChange } = props;

  const entity_names = useAPIv2Result(
    "/vocabulary/entity_type",
    {
      all: "true",
    },
    { unwrapResponse: unwrapEntityTypes }
  );

  console.log(entity_names);
  const onChange = (entity) => {
    console.log(entity);
    onEntityTypeChange(entity);
  };
  let names = [];

  if (entity_names) {
    names = [...entity_names];
  }

  return h(FormGroup, { label: "Entity Type" }, [
    h(MySuggest, {
      items: names,
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

  const refs = useAPIv2Result(
    "/vocabulary/entity_reference",
    { all: "true" },
    { unwrapResponse: unwrapEntityTypes }
  );

  let references = [];
  if (refs) {
    references = [...refs];
  }
  return h("div", [
    h(FormGroup, { label: "Spatial Reference" }, [
      h(MySuggest, { items: references, onChange }),
    ]),
    h(MyNumericInput, {
      label: "Distance from reference (m)",
      value: ref_distance,
      onChange: changeDistance,
    }),
  ]);
}

function geoEntityString(props) {
  const { name, ref_distance, type, ref_unit, ref_datum } = props;

  const geoEntityString = `This sample is from the ${name} ${type}. `;
  const refString = `This sample was taken ${ref_distance} ${ref_unit} from the ${ref_datum} of the geo_entity.`;

  if (name && ref_distance) {
    return geoEntityString + refString;
  } else if (name) {
    return geoEntityString;
  } else {
    return null;
  }
}

export function GeoEntityInterpretation(props) {
  const { entities } = props;
  return h("div", [
    entities.map((ent, i) => {
      const { type, name, fullString, ref_datum, ref_distance, ref_unit } = ent;
      return h("div", { key: i }, [
        h("div.attributes", [
          h.if(name)(ModelAttributeOneLiner, {
            title: "Geologic Entity Name:",
            content: name,
          }),
          h.if(type)(ModelAttributeOneLiner, {
            title: "Geologic Entity Type:",
            content: type,
          }),
          h.if(ref_datum)(ModelAttributeOneLiner, {
            title: "Reference Datum:",
            content: ref_datum,
          }),
          h.if(ref_distance)(ModelAttributeOneLiner, {
            title: "Reference Distance:",
            content: `${ref_distance} ${ref_unit}`,
          }),
        ]),
        h("div.interp", [
          h.if(fullString)(ModelAttributeOneLiner, {
            title: "Interpretation:",
            content: fullString,
          }),
        ]),
      ]);
    }),
  ]);
}

export function GeoEntityText(props) {
  const {
    sample_geo_entity,
    isEditing = true,
    deleteGeoEntity,
  }: {
    sample_geo_entity: sample_geo_entity[];
    isEditing: boolean;
    deleteGeoEntity: (index) => void;
  } = props;
  if (!sample_geo_entity) return null;
  console.log(sample_geo_entity);

  const listofEntityStrings = sample_geo_entity.map((sample_geo_entity) => {
    const { geo_entity, ref_datum, ref_distance, ref_unit } = sample_geo_entity;
    const { type, name } = geo_entity;

    const fullString = geoEntityString({
      name,
      ref_datum,
      ref_distance,
      ref_unit,
      type,
    });

    return { type, name, fullString, ref_datum, ref_distance, ref_unit };
  });
  if (isEditing) {
    return h("div", [
      listofEntityStrings.map((string, index) => {
        return h(GeoEntityTextContainer, {
          geoEntityText: string.fullString,
          geoEntity: sample_geo_entity,
          onClick: () => deleteGeoEntity(index),
        });
      }),
    ]);
  } else {
    return h(GeoEntityInterpretation, { entities: listofEntityStrings });
  }
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

  return h(
    ModelLinkCard,
    { onClick: () => onClick(geoEntity), link: false, isEditing: true },
    [h("h4", [geoEntityText])]
  );
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
  const {
    isEditing = true,
    sample_geo_entity,
    changeGeoEntity,
    deleteGeoEntity,
    initialQuery = null,
  }: {
    isEditing: boolean;
    sample_geo_entity: sample_geo_entity[];
    changeGeoEntity: (g) => void;
    deleteGeoEntity: (g) => void;
    initialQuery: string;
  } = props;
  const defaultState: sample_geo_entity = {
    ref_datum: null,
    ref_distance: null,
    ref_unit: null,
    geo_entity: { type: null, name: initialQuery },
  };
  const [geoEntity, setGeoEntity] = useState<sample_geo_entity>(defaultState);
  console.log(sample_geo_entity);

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

  useEffect(() => {
    if (initialQuery != "") {
      changeGeoName(initialQuery);
    }
  }, [initialQuery]);

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
  };

  const { geo_entity } = geoEntity;
  const { type, name } = geo_entity;

  const content = h("div.geo-entity-card", [
    h("div.geo-entity-drop", [
      h("div.entity", [
        h(SampleGeoEntity, {
          name,
          changeGeoEntity: changeGeoName,
          initialQuery,
        }),
        h(EntityType, { type, onEntityTypeChange: changeGeoType }),
      ]),
      h(GeoSpatialRef, { geoEntity, changeDistance, changeDatum, changeUnit }),
    ]),
    h(Button, { intent: "success", onClick: onSubmitClick }, [
      "Create Geologic Context",
    ]),
  ]);

  if (!isEditing) {
    return h("div", [
      h(GeoEntityText, {
        sample_geo_entity,
        isEditing: false,
      }),
    ]);
  }

  return h("div", [
    h(HelpButton, { content: helpContent, position: "top" }),
    content,
    h(GeoEntityText, { sample_geo_entity, deleteGeoEntity }),
  ]);
}
