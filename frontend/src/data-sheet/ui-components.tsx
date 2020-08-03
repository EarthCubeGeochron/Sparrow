import React, { useEffect, useState, useContext } from "react";
import {
  APIContext,
  APIActions,
  QueryParams,
  APIHookOpts,
} from "@macrostrat/ui-components";
import { Dialog, Button, Classes } from "@blueprintjs/core";
import "./datasheet.modules.css";

export const useAPIResult = function <T>(
  route: string | null,
  params: QueryParams = {},
  opts: APIHookOpts | (<T, U = any>(arg: U) => T) = {}
): T {
  /* React hook for API results, pulled out of @macrostrat/ui-components.
    The fact that this works inline but the original hook doesn't suggests that we
    have overlapping React versions between UI-components and the main codebase.
    Frustrating. */
  const deps = [route, ...Object.values(params ?? {})];

  const [result, setResult] = useState<T | null>(null);

  if (typeof opts === "function") {
    opts = { unwrapResponse: opts };
  }

  const { debounce: _debounce, ...rest } = opts ?? {};
  let { get } = APIActions(useContext(APIContext));

  useEffect(() => {
    const getAPIData = async function () {
      if (route == null) {
        return setResult(null);
      }
      const res = await get(route, params, rest);
      return setResult(res);
    };
    getAPIData();
  }, deps);
  return result;
};

export const SubmitDialog = ({
  onClick,
  content,
  divClass = null,
  className = null,
}) => {
  const [open, setOpen] = useState(false);
  return (
    <div className={divClass}>
      <Button className={className} onClick={() => setOpen(true)}>
        Submit Changes
      </Button>
      <Dialog isOpen={open}>
        <div className={Classes.DIALOG_HEADER}>
          <h3>WARNING</h3>
        </div>
        <div className={Classes.DIALOG_BODY}>
          <p>{content}</p>
        </div>
        <div className={Classes.DIALOG_FOOTER}>
          <Button
            className="save-btn"
            onClick={() => {
              onClick();
              setOpen(false);
            }}
            intent="primary"
          >
            Submit
          </Button>
          <Button
            className="save-btn"
            onClick={() => setOpen(false)}
            intent="danger"
          >
            Cancel
          </Button>
        </div>
      </Dialog>
    </div>
  );
};
