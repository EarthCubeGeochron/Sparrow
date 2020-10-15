import * as React from "react";
import { useState, ReactNode } from "react";
import h from "@macrostrat/hyper";
import { TagInput } from "@blueprintjs/core";

/** component for creating tags from input
 * 
 */

export default function TagInputs() {
  const [tags, setTags] = useState<ReactNode[]>([]);
  const handleOnChange = (e: ReactNode[]) => {
    setTags(e);
  };
  console.log(tags);

  return h(TagInput, {
    values: tags,
    onChange: handleOnChange,
    fill: false,
    placeholder: "Tags can be separated with commas",
  });
}
