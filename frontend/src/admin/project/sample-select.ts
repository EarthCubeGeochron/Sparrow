import { Dialog } from "@blueprintjs/core";
import h from "@macrostrat/hyper";

function SampleSelectDialog(props) {
  const { isOpen } = props;
  return h(Dialog, { isOpen });
}

export { SampleSelectDialog };
