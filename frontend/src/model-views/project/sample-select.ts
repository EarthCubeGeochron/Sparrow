import { Dialog, Classes, Button, Intent } from "@blueprintjs/core";
import { CancelButton } from "@macrostrat/ui-components";
import h from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { SampleCard } from "../sample/detail-card";

function AddSampleArea() {
  const samples = useAPIv2Result("/models/sample", {
    nest: "material",
    not_has: "project",
    per_page: 40,
  });
  if (samples == null) return null;

  return h(
    "div.samples",
    samples.data.map((d) => {
      const { name, id, location_name, material } = d;
      return h(SampleCard, { name, id, location_name, material, link: false });
    })
  );
}

function SampleSelectDialog(props) {
  const { isOpen, onClose } = props;
  return h(Dialog, { isOpen, onClose }, [
    h("div", { className: Classes.DIALOG_HEADER }, [
      h("h4.bp3-heading", "Add samples to project"),
    ]),
    h("div", { className: Classes.DIALOG_BODY }, [h(AddSampleArea)]),
    h("div", { className: Classes.DIALOG_FOOTER }, [
      h("div", { className: Classes.DIALOG_FOOTER_ACTIONS }, [
        h(CancelButton, { onClick: onClose }, "Cancel"),
        h(Button, { intent: Intent.SUCCESS, onClick: onClose }, "Done"),
      ]),
    ]),
  ]);
}

export { SampleSelectDialog };
