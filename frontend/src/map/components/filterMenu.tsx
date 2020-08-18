import { useState } from "react";
import * as React from "react";
import { Menu, MenuItem, Icon, InputGroup, Tag } from "@blueprintjs/core";
import "../cluster.css";
import { SampleFilter } from "../../filter";

export function FilterMenu() {
  const [filterType, setFilterType] = useState("Name");
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

  const filterMenu = (
    <Menu>
      <MenuItem
        intent={filterType == "Name" ? "primary" : null}
        labelElement={filterType == "Name" ? <Icon icon="tick" /> : null}
        onClick={() => setFilterType("Name")}
        text="Name"
      />
      <MenuItem
        intent={filterType == "Material" ? "primary" : null}
        labelElement={filterType == "Material" ? <Icon icon="tick" /> : null}
        onClick={() => setFilterType("Material")}
        text="Material"
      />
      <MenuItem
        intent={filterType == "Location" ? "primary" : null}
        labelElement={filterType == "Location" ? <Icon icon="tick" /> : null}
        onClick={() => setFilterType("Location")}
        text="Location"
      />
      <MenuItem
        intent={filterType == "Sparrow ID" ? "primary" : null}
        labelElement={filterType == "Sparrow ID" ? <Icon icon="tick" /> : null}
        onClick={() => setFilterType("Sparrow ID")}
        text="Sparrow ID"
      />
    </Menu>
  );

  return (
    <div style={{ display: "flex" }}>
      <InputGroup
        placeholder={"Global Filter"}
        onChange={(e) => inputChange(e)}
      />
      <SampleFilter />
    </div>
  );
}
