import { useContext, useState } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import {
  Button,
  Drawer,
  Card,
  Dialog,
  EditableText,
  ButtonGroup,
  Intent,
  Popover,
} from "@blueprintjs/core";
import { DatePicker } from "@blueprintjs/datetime";
import {
  useAPIActions,
  ModelEditorContext,
  ModelEditButton,
  CancelButton,
  SaveButton,
} from "@macrostrat/ui-components";
import { APIV2Context } from "~/api-v2";
import { MySwitch, MinimalNavbar } from "~/components";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export async function getfunc(props) {
  const { url, params } = props;
  const { get } = useAPIActions(APIV2Context);
  try {
    const data = await get(url, params, {});
  } catch (error) {
    console.error(error);
  }
}

export function FormSlider(props) {
  const { content, onClose = () => {}, model } = props;
  const [isOpen, setOpen] = useState(false);

  const changeOpen = () => {
    setOpen(!isOpen);
  };

  const close = () => {
    changeOpen();
    onClose();
  };

  return h("div", [
    h(Card, [
      h(
        Button,
        {
          onClick: changeOpen,
          minimal: true,
          icon: "plus",
          intent: "success",
        },
        [`Create a New ${model}`]
      ),
    ]),
    h(
      Drawer,
      {
        usePortal: true,
        className: "drawer-add",
        title: `Add a new ${model}`,
        isOpen,
        onClose: close,
        isCloseButtonShown: true,
      },
      [content, h(Button, { onClick: close, intent: "danger" }, ["Cancel"])]
    ),
  ]);
}

function isLetter(char) {
  if (char.toUpperCase() != char.toLowerCase()) {
    return true;
  } else {
    return false;
  }
}

export const isTitle = (search) => {
  let i = 0;
  for (let char of search) {
    if (isLetter(char)) {
      i += 1;
    }
  }
  if (i / search.length > 0.7) {
    return true;
  } else {
    return false;
  }
};

export const SubmitDialog = (props) => {
  const { open, changeOpen, goToModel, modelName } = props;

  return h(Dialog, { isOpen: open, style: { maxWidth: "300px" } }, [
    h(
      "div",
      {
        style: {
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        },
      },
      [
        h("h4", ["Are you sure you want to submit?"]),
        h("div", [
          h(
            Button,
            {
              intent: "success",
              onClick: goToModel,
              style: { marginRight: "5px" },
            },
            [`Create New ${modelName}`]
          ),
          h(Button, { intent: "danger", onClick: changeOpen }, ["Cancel"]),
        ]),
      ]
    ),
  ]);
};

export const SubmitButton = (props) => {
  const { postData, modelName } = props;
  const [open, setOpen] = useState(false);

  const changeOpen = () => {
    setOpen(!open);
  };

  const goToModel = () => {
    postData();
  };

  return h("div", { style: { marginTop: "5px" } }, [
    h(SubmitDialog, { open, changeOpen, goToModel, modelName }),
    h(
      Button,
      {
        onClick: changeOpen,
        intent: "primary",
      },
      ["Done"]
    ),
  ]);
};

export function ModelEditableText(props) {
  let {
    multiline,
    field,
    placeholder,
    is,
    editOn = false,
    onChange = () => {},
    value = null,
    ...rest
  } = props;
  const el = is || "div";
  if (placeholder == null) {
    placeholder = "Add a " + field;
  }

  if (!editOn) {
    const { model, actions, isEditing } = useContext(ModelEditorContext);

    // Show text with primary intent if changes have been made
    const intent = actions.hasChanges(field) ? "success" : null;

    console.log(model);

    return h(el, rest, [
      h.if(isEditing)(EditableText, {
        className: `model-edit-text field-${field}`,
        multiline,
        placeholder,
        intent,
        onChange: actions.onChange(field),
        value: model[field],
      }),
      h.if(!isEditing)("span", model[field]),
    ]);
  }
  const { id, onConfirm } = rest;
  return h(el, [
    h(EditableText, {
      className: "model-edit-text",
      multiline,
      placeholder,
      onChange,
      value,
      id,
      onConfirm,
    }),
  ]);
}

const ToInfinityDate = (date) => {
  const newYear = date.getFullYear() + 3000;
  const month = date.getMonth();
  const day = date.getDay();
  return new Date(newYear, month, day);
};

export const EmbargoDatePick = (props) => {
  const { onChange, embargo_date, active = true } = props;
  // need to add an un-embargo if data is embargoed. And an infinite embargo
  const embargoDate = embargo_date ? new Date(embargo_date) : null;

  let today = new Date();
  let tomorrow = new Date();
  tomorrow.setDate(today.getDate() + 1);

  const embargoed = embargoDate ? true : false;

  const infinite =
    embargoDate && embargoDate.getFullYear() === today.getFullYear() + 3000
      ? true
      : false;

  const text =
    embargoDate != null
      ? infinite
        ? "Embargoed Indefinitely"
        : `Embargoed Until: ${embargoDate.toISOString().split("T")[0]}`
      : "Public";
  const icon = embargoDate != null ? "lock" : "unlock";

  const switchChange = () => {
    if (infinite) {
      onChange(null);
    } else {
      onChange(ToInfinityDate(today));
    }
  };

  const Content = () => {
    return h(Card, [
      h(DatePicker, {
        minDate: new Date(),
        maxDate: new Date(2050, 1, 1),
        onChange: (e) => {
          let date = e.toISOString().split("T")[0];
          onChange(e);
        },
      }),
      h("div", [
        "Emargo Forever: ",
        h(MySwitch, {
          checked: infinite,
          onChange: switchChange,
        }),
      ]),
      h(
        Button,
        {
          disabled: !embargoed,
          onClick: () => onChange(null),
          minimal: true,
        },
        ["Make Public"]
      ),
    ]);
  };

  return h("div.embargo-editor", [
    h(Popover, { content: h(Content), disabled: !active }, [
      h(Button, {
        text,
        minimal: true,
        rightIcon: icon,
        intent: Intent.SUCCESS,
        disabled: !active,
      }),
    ]),
  ]);
};

export const EditStatusButtons = function (props) {
  const { hasChanges, isEditing, onClickCancel, onClickSubmit, ...rest } =
    props;

  const changed = hasChanges();
  return h("div.edit-status-controls", [
    h.if(!isEditing)(ModelEditButton, { minimal: true, ...rest }, "Edit"),
    h.if(isEditing)(ButtonGroup, { minimal: true, ...rest }, [
      h(
        SaveButton,
        {
          disabled: !changed,
          onClick: onClickSubmit,
        },
        "Save"
      ),
      h(
        CancelButton,
        {
          intent: changed ? "warning" : "none",
          onClick: onClickCancel,
        },
        "Done"
      ),
    ]),
  ]);
};

export const EditNavBar = function (props) {
  const { editButtons, embargoEditor, header } = props;
  return h(MinimalNavbar, { className: "project-editor-navbar" }, [
    h("h4", header),
    editButtons,
    embargoEditor,
  ]);
};

export function DataSheetButton() {
  const url = "/admin/data-sheet";
  const handleClick = (e) => {
    e.preventDefault();
    window.location.href = url;
  };

  return h("div", { style: { padding: "0px 5px 5px 0px" } }, [
    h(Button, { onClick: handleClick, minimal: true }, ["Data Sheet View"]),
  ]);
}

export const pluralize = function (term, arrayOrNumber) {
  let count = arrayOrNumber;
  if (Array.isArray(arrayOrNumber)) {
    count = arrayOrNumber.length;
  }
  if (count > 1) {
    if (term.slice(-1) == "s") {
      term += "es";
    } else {
      term += "s";
    }
  }
  return term;
};
