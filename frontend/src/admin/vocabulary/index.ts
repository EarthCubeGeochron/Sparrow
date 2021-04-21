import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { useState } from "react";
import {
  Spinner,
  Card,
  Button,
  ButtonGroup,
  Menu,
  MenuItem,
  Popover,
} from "@blueprintjs/core";
import { Switch, Route, useRouteMatch } from "react-router-dom";
import { MinimalNavbar, NavButton } from "~/components";
import { TermCard } from "@earthdata/schema-linker";

import styles from "./module.styl";
const h = hyperStyled(styles);

enum Term {
  PARAMETER = "parameter",
  MATERIAL = "material",
}

function VocabularyList(props) {
  const { authority, exclude, local = false, term = Term.PARAMETER } = props;

  const params = useAPIv2Result(`/vocabulary/${term}`, {
    all: true,
    authority,
  });
  if (params == null) return h(Spinner);
  let { data } = params;
  if (exclude != null) data = data.filter((d) => d.authority != exclude);
  if (local)
    data = data.filter((d) => d.authority == null || d.authority != "Sparrow");

  return h("div.list-column", [
    h.if(authority != null)("h2", authority),
    h(
      "div.vocabulary-list",
      data.map((d) => h(TermCard, { data: d }))
    ),
  ]);
}

function NavMenu() {
  return h(ButtonGroup, { minimal: true }, [
    h(NavButton, { to: "/admin/terms/parameter" }, "Parameter"),
    h(NavButton, { to: "/admin/terms/material" }, "Material"),
  ]);
}

function AuthorityMenu({ authority, setAuthority }) {
  const auth = useAPIv2Result("/vocabulary/authority", { all: true }, {});
  if (auth == null) return null;
  const content = h(
    Menu,
    {},
    auth.data.map((d) =>
      h(MenuItem, {
        onClick() {
          setAuthority(d.id);
        },
        text: d.id,
      })
    )
  );

  return h(
    Popover,
    { content },
    h(Button, { minimal: true }, h(["Authority: ", h("b", authority)]))
  );
}

function VocabularyPanel({ authority }) {
  const term = useRouteMatch()?.params?.term ?? "parameter";

  return h("div.vocabulary-panel", [
    h(VocabularyList, { local: true, term }),
    h(VocabularyList, { authority, term }),
  ]);
}

export function VocabularyPage() {
  const [authority, setAuthority] = useState("Sparrow");
  const base = "/admin/terms";

  return h("div.vocabulary-page", {}, [
    h(MinimalNavbar, { className: "navbar" }, [
      h("h4", "Terms"),
      h(NavMenu),
      h("div.navbar-spacer"),
      h(AuthorityMenu, { authority, setAuthority }),
    ]),
    h(Switch, [
      h(
        Route,
        {
          path: base + "/:term",
        },
        h(VocabularyPanel, { authority })
      ),
    ]),
  ]);
}
