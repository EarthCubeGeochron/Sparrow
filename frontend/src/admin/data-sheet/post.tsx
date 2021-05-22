/**
 * Issues with POST data.
 *
 * How to handle Project name and publicaiton DOI.
 *  CASE 1: Copying DOI or Project Name into new row. The ID's aren't associated with the row
 *  CASE 2: Adding new unique DOI's or Project Names that don't exist, no ID associated period
 *
 *  Case 1 SOLUTION:
 *      If the original DOI or Paper name WASN'T changed before copying, I can send without the ID
 *      and do a database check on the backend similar to how I handle the material.
 *
 *      If the original DOI or Paper WAS changed before copying. This would mean it would go through as
 *      edit. So maybe the backend can do a check and some logic stuff.
 *
 *
 *  Case 2 SOLUTION:
 *      Run a database check on the backend and then add in new info, associated with sample id.
 *      NOTE: there is no publication_sample table... probably should be.
 *
 * The bigger issue is how do we store publication info with respect to sample. Esp if the sample doesn't
 * have an associated project?
 */

import axios from "axios";
import { APIV2Context } from "~/api-v2";
import { APIHelpers } from "@macrostrat/ui-components";
import { useContext } from "react";

export function postData(data) {
  const post_data = JSON.stringify(data);
  const { buildURL } = APIHelpers(useContext(APIV2Context));

  const url = buildURL("/datasheet/edits");
  console.log(url);

  axios
    .post(url, post_data)
    .then(function(response) {
      console.log(response);
    })
    .catch(function(error) {
      console.log(error);
    });
}
