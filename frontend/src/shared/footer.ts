import h from "react-hyperscript";
import { Frame } from "sparrow/frame";
import { Markdown } from "@macrostrat/ui-components";
import { InsetText } from "app/components/layout";
import footerText from "./footer-text.md";

const PageFooter = (props) =>
  h(
    Frame,
    { id: "pageFooter" },
    h(InsetText, null, h(Markdown, { src: footerText }))
  );

export { PageFooter };
