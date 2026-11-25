import { usePostgRESTActions } from "./postgrest";

/** Columns each model view can write. Links to other records are not
 * editable yet: their join tables (project_researcher, project_publication,
 * project_sample) have no API views, and the session view is not updatable. */
export const editableFields = {
  sample: [
    "name",
    "material",
    "member_of",
    "location",
    "location_name",
    "depth",
    "elevation",
    "embargo_date",
  ],
  project: ["name", "description", "embargo_date"],
};

type EditableModel = keyof typeof editableFields;

function pick(obj: object, keys: string[]) {
  const res = {};
  for (const k of keys) {
    if (k in obj) res[k] = obj[k];
  }
  return res;
}

export function useModelPersist(model: EditableModel) {
  /** A `persistChanges` for ModelEditor that writes through PostgREST */
  const { update, insert, remove } = usePostgRESTActions();
  const fields = editableFields[model];

  return async function persistChanges(updatedModel, changeset) {
    const { id } = updatedModel;
    const body = pick(changeset, fields);
    if (Object.keys(body).length > 0) {
      await update(`/${model}`, { id: `eq.${id}` }, body);
    }
    if (changeset.tags_tag != null) {
      const link = `/${model}_tag`;
      const idColumn = `${model}_id`;
      await remove(link, { [idColumn]: `eq.${id}` });
      const rows = changeset.tags_tag.map((tag) => ({
        tag_id: tag.id,
        [idColumn]: id,
      }));
      if (rows.length > 0) await insert(link, rows);
    }
    // Only what was written is merged back into the editor's saved state
    return pick(changeset, [...fields, "tags_tag"]);
  };
}
