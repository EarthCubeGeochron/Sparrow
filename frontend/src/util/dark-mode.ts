import h, { compose } from "@macrostrat/hyper";
import { useEffect } from "react";
import { DarkModeProvider, inDarkMode } from "@macrostrat/ui-components";

function DarkModeWrapper(props) {
  const isDark = inDarkMode();
  const className = isDark ? "bp4-dark" : null;
  // To make modals etc. work, we need to add the dark-mode class to the body
  useEffect(() => {
    if (isDark) {
      document.body.classList.add("bp4-dark");
    } else {
      document.body.classList.remove("bp4-dark");
    }
  }, [isDark]);
  return h("div", { className, ...props });
}

const DarkModeManager = compose(DarkModeProvider, DarkModeWrapper);

export { DarkModeManager };
