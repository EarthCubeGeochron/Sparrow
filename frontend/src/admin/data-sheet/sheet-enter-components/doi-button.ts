/**
 * This is some bandage code for handling multiple DOI's in one cell.
 */
import React, { useState, useContext } from "react";
import { NavButton } from "~/components";
import h from "@macrostrat/hyper";
import { DataEditor } from "react-datasheet/lib";

function DoiProjectButton(props) {
  const { row, col, data, value } = props;
  if (data[row]["project_id"] == null) return;
  //console.log(value.split(",").length);
  console.log(row);
  if (value.split(",").length > 1) {
    const projectId = data[row]["project_id"];
    return h(NavButton, { to: "/admin/project/" + projectId }, [
      "Go to Project",
    ]);
  }
  return h(DataEditor, { ...props });
}

export { DoiProjectButton };
