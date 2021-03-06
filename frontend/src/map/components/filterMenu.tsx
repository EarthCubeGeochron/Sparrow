import { useState } from "react";
import * as React from "react";
import { Menu, MenuItem, Icon, InputGroup, Tag } from "@blueprintjs/core";
import "../cluster.css";
import { SampleFilter } from "../../filter";

export function FilterMenu({ hide = true, on_map }) {
  const [tags, setTags] = useState([]);

  const inputChange = (e) => {
    const newTags = tags.concat(e.target.value);
    setTags(newTags);
    console.log(tags);
  };

  const tagElements = tags.map((tag) => {
    const onRemove = () => setTags(tags.filter((t) => t !== tag));
    return <Tag onRemove={onRemove}>{tag}</Tag>;
  });

  return (
    <div>
      {hide ? null : (
        <div style={{ display: "flex" }}>
          <InputGroup
            placeholder={"Global Filter"}
            onChange={(e) => inputChange(e)}
          />
          <SampleFilter on_map={on_map} />
        </div>
      )}
    </div>
  );
}
