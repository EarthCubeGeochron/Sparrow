import * as React from "react";
import {
  Menu,
  MenuItem,
  Popover,
  Tooltip,
  Button,
  Position,
  Icon,
} from "@blueprintjs/core";
import "../cluster.css";

export const MapNav = () => {
  const pages = [
    { name: "Home", link: "/", icon: "home" },
    { name: "Sample", link: "/catalog/sample", icon: "circle" },
    { name: "Project", link: "/catalog/project", icon: "clipboard" },
    { name: "Session", link: "/catalog/session", icon: "heatmap" },
  ];
  const dropMenu = (
    <Menu>
      {pages.map((Ob) => {
        const { name, link, icon } = Ob;
        return (
          <MenuItem
            key={name}
            text={name}
            href={link}
            labelElement={<Icon icon={icon} />}
          />
        );
      })}
    </Menu>
  );
  return (
    <div>
      <div className="mappagemenu">
        <Popover content={dropMenu} minimal={true} position={Position.BOTTOM}>
          <Tooltip content="Navigate">
            <Button minimal={true}>
              <Icon icon="menu" />
            </Button>
          </Tooltip>
        </Popover>
      </div>
    </div>
  );
};
