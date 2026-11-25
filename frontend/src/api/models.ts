/**
 * Records shaped the way the model views expect, read from PostgREST.
 *
 * The session, project, analysis and datum views wrap `core_view` views, and
 * PostgREST 11 finds no foreign keys through them, so they cannot be embedded.
 * Their related records are fetched separately and joined here.
 */
import { useAuth } from "~/auth/context";
import {
  QueryParams,
  getAllRows,
  inList,
  quote,
  usePostgRESTResult,
  useQueryResult,
} from "./postgrest";

type Row = { [k: string]: any };

function isObject(v): v is Row {
  return v != null && typeof v === "object";
}

export function asGeometry(value) {
  /** PostGIS columns arrive as GeoJSON; anything else is treated as missing */
  if (isObject(value) && Array.isArray(value.coordinates)) return value;
  return null;
}

function unwrapTags(links: Row[] | null): Row[] {
  return (links ?? []).map((d) => d.tag).filter((d) => d != null);
}

export function normalizeSession(row: Row): Row {
  let { instrument, sample, project, publication } = row;
  if (!isObject(instrument)) {
    instrument =
      row.instrument_name == null
        ? null
        : { id: row.instrument, name: row.instrument_name };
  }
  if (!isObject(sample) && row.sample_id != null) {
    sample = { id: row.sample_id, name: row.sample_name };
  }
  if (!isObject(project) && row.project_id != null) {
    project = { id: row.project_id, name: row.project_name };
  }
  return {
    ...row,
    instrument,
    sample: sample ?? null,
    project: project ?? null,
    publication: isObject(publication) ? publication : null,
    analysis: row.analysis ?? [],
    tags_tag: row.tags_tag ?? unwrapTags(row.session_tag),
  };
}

export function normalizeSample(row: Row): Row {
  const session = (row.session ?? []).map(normalizeSession);
  const projects = new Map();
  for (const s of session) {
    if (s.project != null) projects.set(s.project.id, s.project);
  }
  return {
    ...row,
    location: asGeometry(row.location ?? row.geometry),
    session,
    project: row.project ?? Array.from(projects.values()),
    tags_tag: row.tags_tag ?? row.tag ?? [],
    // geo_entity and sample_geo_entity are not exposed by the API
    sample_geo_entity: row.sample_geo_entity ?? [],
  };
}

export function normalizeProject(row: Row): Row {
  const samples = row.sample ?? row.samples ?? [];
  return {
    ...row,
    publication: row.publication ?? row.publications ?? [],
    researcher: row.researcher ?? row.researchers ?? [],
    sample: samples.map(normalizeSample),
    session: (row.session ?? []).map(normalizeSession),
    tags_tag: row.tags_tag ?? unwrapTags(row.project_tag),
  };
}

function first(rows: Row[] | null): Row | null {
  if (rows == null || rows.length == 0) return null;
  return rows[0];
}

async function fetchSession(get, id): Promise<Row | null> {
  // The session view repeats a session once per linked data file
  const session = first(await get("/session", { id: `eq.${id}` }));
  if (session == null) return null;
  const [tags, analysis, sample, publication] = await Promise.all([
    get("/session_tag", { session_id: `eq.${id}`, select: "tag(*)" }),
    getAllRows(get, "/analysis", {
      session_id: `eq.${id}`,
      select: "analysis_id",
    }),
    session.sample_id == null
      ? null
      : get("/sample", { id: `eq.${session.sample_id}` }),
    session.publication_id == null
      ? null
      : get("/publication", { id: `eq.${session.publication_id}` }),
  ]);
  return normalizeSession({
    ...session,
    session_tag: tags,
    analysis: analysis ?? [],
    sample: first(sample) ?? undefined,
    publication: first(publication),
  });
}

async function fetchSample(get, id): Promise<Row | null> {
  const sample = first(
    await get("/sample", { id: `eq.${id}`, select: "*,tag(*)" })
  );
  if (sample == null) return null;
  const session = await getAllRows(get, "/session", {
    sample_id: `eq.${id}`,
    order: "date.desc",
  });
  return normalizeSample({ ...sample, session: uniqueById(session ?? []) });
}

async function fetchProject(get, id): Promise<Row | null> {
  const project = first(await get("/project", { id: `eq.${id}` }));
  if (project == null) return null;
  const [tags, sessions] = await Promise.all([
    get("/project_tag", { project_id: `eq.${id}`, select: "tag(*)" }),
    getAllRows(get, "/session", { project_id: `eq.${id}`, order: "date.desc" }),
  ]);
  const session = uniqueById(sessions ?? []);
  // Sessions carry only the sample's name; attach the full sample records
  const samples = new Map(
    (project.samples ?? []).map((s) => [s.id, normalizeSample(s)])
  );
  for (const s of session) {
    s.sample = samples.get(s.sample_id) ?? undefined;
  }
  return normalizeProject({ ...project, session, project_tag: tags });
}

function uniqueById(rows: Row[]): Row[] {
  const seen = new Set();
  return rows.filter((d) => {
    if (seen.has(d.id)) return false;
    seen.add(d.id);
    return true;
  });
}

export function useSessionModel(id) {
  return useQueryResult(id == null ? null : (get) => fetchSession(get, id), [
    id,
  ]);
}

export function useSampleModel(id) {
  return useQueryResult(id == null ? null : (get) => fetchSample(get, id), [
    id,
  ]);
}

export function useProjectModel(id) {
  return useQueryResult(id == null ? null : (get) => fetchProject(get, id), [
    id,
  ]);
}

export function useSubSamples(sample_id) {
  return usePostgRESTResult(
    sample_id == null ? null : "/sample",
    { member_of: `eq.${sample_id}`, order: "name" },
    { unwrap: (rows) => rows.map(normalizeSample) }
  );
}

export function usePublication(id) {
  return usePostgRESTResult(
    id == null ? null : "/publication",
    { id: `eq.${id}` },
    { unwrap: first }
  );
}

export function useAllTags() {
  return usePostgRESTResult("/tag", { order: "name" }, { all: true });
}

interface DataFileLinkQuery {
  sample_id?: number[];
  session_id?: number[];
  analysis_id?: number[];
}

export function useDataFileLinks(query: DataFileLinkQuery) {
  /** Files linked to any of these records; data files are visible to admins only */
  const { token } = useAuth();
  const clauses = [];
  for (const [col, ids] of Object.entries(query)) {
    if (ids != null && ids.length > 0) clauses.push(`${col}.${inList(ids)}`);
  }
  const params: QueryParams = {
    select: "*,data_file(basename,file_mtime,type_id)",
    or: `(${clauses.join(",")})`,
    order: "date.desc",
  };
  const route = clauses.length > 0 && token != null ? "/data_file_link" : null;
  return usePostgRESTResult(route, params, {
    unwrap: (rows) => rows.map(flattenDataFileLink),
  });
}

function flattenDataFileLink(link: Row): Row {
  let model = null;
  let model_id = null;
  for (const m of ["session", "sample", "analysis"]) {
    if (link[`${m}_id`] != null) {
      model = m;
      model_id = link[`${m}_id`];
    }
  }
  return {
    ...link,
    ...(link.data_file ?? {}),
    type: link.data_file?.type_id,
    model,
    model_id,
  };
}

async function fetchDataFile(get, file_hash): Promise<Row | null> {
  const file = first(
    await get("/data_file", {
      file_hash: `eq.${file_hash}`,
      select: "*,data_file_link(*,sample(id,name,material,location))",
    })
  );
  if (file == null) return null;
  const links = file.data_file_link ?? [];
  const sessionIDs = links.map((d) => d.session_id).filter((d) => d != null);
  let sessions = [];
  if (sessionIDs.length > 0) {
    sessions = (await get("/session", { id: inList(sessionIDs) })) ?? [];
  }
  const sessionIndex = new Map(
    uniqueById(sessions).map((s) => [s.id, normalizeSession(s)])
  );
  return {
    ...file,
    type: file.type_id,
    data_file_link: links.map((l) => ({
      ...l,
      sample: l.sample == null ? null : normalizeSample(l.sample),
      session: sessionIndex.get(l.session_id) ?? null,
    })),
  };
}

export function useDataFile(file_hash) {
  return useQueryResult(
    file_hash == null ? null : (get) => fetchDataFile(get, file_hash),
    [file_hash]
  );
}

/* Filters from the admin list panels, translated to PostgREST */

interface ModelFilterSpec {
  search: string[];
  date?: string;
  doi?: string;
  publicity?: "is_public" | "embargo_date";
}

const filterSpecs: { [model: string]: ModelFilterSpec } = {
  project: {
    search: ["name", "description"],
    publicity: "is_public",
  },
  sample: {
    search: ["name", "material", "igsn", "lab_id", "location_name"],
    publicity: "embargo_date",
  },
  session: {
    search: [
      "name",
      "sample_name",
      "project_name",
      "technique",
      "target",
      "instrument_name",
    ],
    date: "date",
    publicity: "is_public",
  },
  publication: { search: ["title", "doi", "author", "journal"], doi: "doi" },
  researcher: { search: ["name", "orcid"] },
  data_file: { search: ["basename", "file_path"], date: "file_mtime" },
};

export function filterParams(model: string, filters: Row = {}): QueryParams {
  /** Combine the admin filter state into one `and=` expression */
  const spec = filterSpecs[model];
  if (spec == null) return {};
  const clauses: string[] = [];

  const search = filters.search ?? filters.like;
  if (search != null && search != "") {
    const pattern = quote(`*${search}*`);
    const terms = spec.search.map((col) => `${col}.ilike.${pattern}`);
    clauses.push(`or(${terms.join(",")})`);
  }

  if (filters.public != null && spec.publicity != null) {
    const isPublic = String(filters.public) == "true";
    if (spec.publicity == "is_public") {
      clauses.push(`is_public.is.${isPublic}`);
    } else {
      const now = quote(new Date().toISOString());
      clauses.push(
        isPublic
          ? `or(embargo_date.is.null,embargo_date.lt.${now})`
          : `embargo_date.gte.${now}`
      );
    }
  }

  let dates = filters.date_range;
  if (typeof dates == "string") dates = dates.split(",");
  if (Array.isArray(dates) && spec.date != null) {
    const [start, end] = dates;
    if (start) clauses.push(`${spec.date}.gte.${quote(start)}`);
    if (end) clauses.push(`${spec.date}.lte.${quote(end)}`);
  }

  if (filters.doi_like && spec.doi != null) {
    clauses.push(`${spec.doi}.ilike.${quote(`*${filters.doi_like}*`)}`);
  }

  if (clauses.length == 0) return {};
  return { and: `(${clauses.join(",")})` };
}
