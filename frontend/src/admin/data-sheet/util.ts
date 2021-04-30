const needs_sample_id = ["name", "material", "longitude", "latitude"];
const needs_project_id = ["proj_name"];
const needs_pub_id = ["DOI"];

/**
 * @description Checks and adds 1 of 3 possible ids to edit objects as well as adds the necesary data
 *
 * @param list : [{row: number, key:string}]
 * @param data : [{state}]
 */
function addNecesaryFields(list, data) {
  const edits_list = [];

  for (let i = 0; i < list.length; i++) {
    const { row, key } = list[i];
    if (key == "longitude") {
      edits_list.push({
        id: data[row]["id"],
        [key]: data[row][key],
        latitude: data[row]["latitude"],
        project_id: data[row]["proj_id"],
      });
    }
    if (key == "latitude") {
      edits_list.push({
        id: data[row]["id"],
        [key]: data[row][key],
        longitude: data[row]["longitude"],
        project_id: data[row]["proj_id"],
      });
    }
    edits_list.push({
      id: data[row]["id"],
      [key]: data[row][key],
      project_id: data[row]["proj_id"],
      // publication_id: data[row]["pub_id"], d
    });
    // } else if (needs_project_id.includes(key)) {
    //   edits_list.push({
    //     project_id: data[row]["proj_id"],
    //     [key]: data[row][key],
    //   });
    // } else if (needs_pub_id.includes(key)) {
    //   edits_list.push({
    //     publication_id: data[row]["pub_id"],
    //     [key]: data[row][key],
    //   });
    // }
  }
  return edits_list;
}

function combineLikeIds(list) {
  /**
   * Takes the edits objects that are single edits with ids and combines them on id
   */
  for (let i = 0; i < list.length; i++) {
    for (let e = 0; e < list.length; e++) {
      if (i != e) {
        if (list[i]["id"] == list[e]["id"]) {
          list[i] = { ...list[i], ...list[e] };
          list.splice(e, 1);
        }
      }
    }
  }
  return list;
}

export { combineLikeIds, addNecesaryFields };
