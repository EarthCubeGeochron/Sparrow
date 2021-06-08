import { useReducer } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { Button, InputGroup, FormGroup, Popover } from "@blueprintjs/core";
import { TwitterPicker } from "react-color";
import { randomHexColor } from "../misscel";
import { tag_reducer, tagBody } from "./types";
import { TagBody } from "./tag-body";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

const tagReducer = (state, action) => {
  switch (action.type) {
    case tag_reducer.NAME:
      return {
        ...state,
        name: action.payload.name,
      };
    case tag_reducer.DESCRIPTION:
      return {
        ...state,
        description: action.payload.description,
      };
    case tag_reducer.HEX_COLOR:
      return {
        ...state,
        color: action.payload.color,
      };
    default:
      throw new Error("What does this mean?");
  }
};

interface tagEditor extends tagBody {
  onSubmit: (e) => void;
  onCancel: () => void;
}

function TagEditor(props: tagEditor) {
  const { name, description, color, onSubmit, onCancel } = props;
  const [tag, dispatch] = useReducer(tagReducer, { name, description, color });

  const changeName = (e) => {
    dispatch({ type: tag_reducer.NAME, payload: { name: e.target.value } });
  };
  const changeDescription = (e) => {
    dispatch({
      type: tag_reducer.DESCRIPTION,
      payload: { description: e.target.value },
    });
  };

  const changeColor = (color) => {
    dispatch({
      type: tag_reducer.HEX_COLOR,
      payload: { color: color.hex },
    });
  };

  const clickRandomColor = () => {
    const color = randomHexColor();
    dispatch({
      type: tag_reducer.HEX_COLOR,
      payload: { color },
    });
  };

  const clickSubmit = () => {
    onSubmit(tag);
  };

  const clickCancel = () => {
    onCancel();
  };

  const colors = [
    "#A82A2A",
    "#B83211",
    "#752F75",
    "#2458B3",
    "#00998C",
    "#238C2C",
    "#F2B824",
    "#FF7373",
    "#FF6E4A",
    "#C274C2",
    "#669EFF",
    "#2EE6D6",
    "#62D96B",
    "#FFC940",
    "#7157D9",
    "#EBF1F5",
    "#293742",
  ];

  return h("div", [
    h(TagBody, {
      name: tag.name,
      description: tag.description,
      color: tag.color,
    }),
    h("div.tag-creator", [
      h(FormGroup, { label: "Tag Name" }, [
        h(InputGroup, { onChange: changeName, value: tag.name }),
      ]),
      h(FormGroup, { label: "Tag Description" }, [
        h(InputGroup, { onChange: changeDescription, value: tag.description }),
      ]),
      h("div.color-picker", [
        h(Button, {
          icon: "random",
          style: { backgroundColor: tag.color },
          onClick: clickRandomColor,
        }),
        h(
          Popover,
          {
            content: h(TwitterPicker, {
              color: tag.color,
              onChangeComplete: changeColor,
              triangle: "hide",
              colors,
            }),
          },
          [h(InputGroup, { value: tag.color, onChange: () => {} })]
        ),
      ]),
      h("div", [
        h(
          Button,
          { onClick: clickCancel, style: { marginRight: "10px" } },
          "Cancel"
        ),
        h(Button, { onClick: clickSubmit, intent: "success" }, "Submit"),
      ]),
    ]),
  ]);
}

export { TagEditor };
