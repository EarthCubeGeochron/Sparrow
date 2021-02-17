import { Dialog, Classes, Button, Intent, InputGroup } from "@blueprintjs/core";
import { CancelButton, useModelEditor } from "@macrostrat/ui-components";
import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { SampleCard } from "../sample/detail-card";
import { useState } from "react";
import styles from "./sample-select.styl";

const h = hyperStyled(styles);

function AddSampleArea(samples) {
  const [sta, setSta] = useState([]);

  const { model, actions } = useModelEditor();
  console.log(model.samples);

  if (model.samples == null) {
    actions.updateState({
      model: { samples: { $set: [] } },
    });
  }

  const handleClickAdd = (id, name) => {
    const newSample = [{ id: id, name: name }];
    setSta([...sta, ...newSample]);
  };

  const handleClickUnAdd = (index) => {
    const newSta = [...sta];
    newSta.splice(index, 1);
    setSta([...newSta]);
  };

  return h("div", [
    h("div.dialog-container", [
      h("div", [
        h("h4", ["Samples from Sparrow"]),
        h(
          "div.samples",
          samples.samples.slice(0, 5).map((d) => {
            const { name, id } = d;
            return h("div.add-sample", [
              h(
                "div.add-sample-btn",
                { onClick: () => handleClickAdd(id, name) },
                [name]
              ),
            ]);
          })
        ),
      ]),
      h("div", [
        h("h4", ["Samples To Add"]),
        sta.length > 0
          ? sta.map((d, index) => {
              const { name, id } = d;
              return h(
                "div.remove-sample-btn",
                { onClick: () => handleClickUnAdd(index) },
                [name]
              );
            })
          : null,
      ]),
    ]),
    // h("div.apply-btn", [h(Button, { intent: Intent.PRIMARY }, "Apply")]),
  ]);
}

function SearchSampleArea(props) {
  const [search, setSearch] = useState("");

  const samples = useAPIv2Result("/models/sample", {
    nest: "material",
    like: search,
  });

  return h("div", [
    h(InputGroup, {
      onChange: (e) => setSearch(e.target.value),
      value: search,
      placeholder: "Search for Sample",
    }),
    samples ? h(AddSampleArea, { samples: samples.data }) : null,
  ]);
}

function SampleSelectDialog(props) {
  const { isOpen, onClose } = props;

  const { model, actions } = useModelEditor();

  return h(Dialog, { isOpen, onClose }, [
    h("div", { className: Classes.DIALOG_HEADER }, [
      h("h4.bp3-heading", "Add samples to project"),
    ]),
    h("div", { className: Classes.DIALOG_BODY }, [h(SearchSampleArea)]),
    h("div", { className: Classes.DIALOG_FOOTER }, [
      h("div", { className: Classes.DIALOG_FOOTER_ACTIONS }, [
        h(CancelButton, { onClick: onClose }, "Cancel"),
        h(Button, { intent: Intent.SUCCESS, onClick: onClose }, "Done"),
      ]),
    ]),
  ]);
}

export { SampleSelectDialog };
