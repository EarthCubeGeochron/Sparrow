import React from "react";
import Toggle from "react-toggle";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import clsx from "clsx";
import styles from "./styles.module.css";
import { Icon } from "@blueprintjs/core";
import { IconNames } from "@blueprintjs/icons";

export default function (props) {
  const { isClient } = useDocusaurusContext();
  return (
    <Toggle
      disabled={!isClient}
      icons={{
        checked: <Icon icon="moon" color="#cccccc" iconSize={16} />,
        unchecked: <Icon icon="flash" color="#cccccc" iconSize={16} />,
      }}
      {...props}
    />
  );
}
