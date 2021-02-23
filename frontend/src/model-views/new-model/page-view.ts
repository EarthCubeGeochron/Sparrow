import { AddSampleCard } from "../sample/detail-card";
import { Button, Dialog, Tooltip } from "@blueprintjs/core";
import {
  ProjectSamples,
  ProjectPublications,
  ProjectResearchers,
} from "../project/page";
import { hyperStyled } from "@macrostrat/hyper";
import styles from "./module.styl";

/**
 * Utils and components for on Page View Editing and Viewing
 */

const h = hyperStyled(styles);

export const AddCard = (props) => {
  const { onClick, model } = props;
  return h(
    Tooltip,
    { content: `Select from exisitng ${model}s` },
    h(AddSampleCard, { onClick, icon_name: "plus" })
  );
};

export const SampleAdd = (props) => {
  const {
    onClickDelete,
    onClickList,
    data,
    rightElement,
    isEditing = true,
    setID = () => {},
  } = props;

  return h("div", [
    h("div", [
      h(ProjectSamples, {
        data,
        link: false,
        isEditing,
        onClick: onClickDelete,
        setID,
        rightElement,
      }),
      h.if(isEditing)(AddCard, {
        model: "sample",
        onClick: onClickList,
      }),
    ]),
  ]);
};

export const PubAdd = (props) => {
  const {
    onClickDelete,
    onClickList,
    data,
    rightElement,
    isEditing = true,
  } = props;
  return h("div", [
    h("div", [
      h(ProjectPublications, {
        data,
        isEditing,
        onClick: onClickDelete,
        rightElement,
      }),
      h.if(isEditing)(AddCard, {
        model: "publication",
        onClick: onClickList,
      }),
    ]),
  ]);
};

export const ResearcherAdd = (props) => {
  const {
    onClickDelete,
    onClickList,
    data,
    rightElement,
    isEditing = true,
  } = props;

  return h("div", [
    h(ProjectResearchers, {
      onClick: onClickDelete,
      data,
      isEditing,
      rightElement,
    }),
    h.if(isEditing)(AddCard, {
      model: "researcher",
      onClick: onClickList,
    }),
  ]);
};
