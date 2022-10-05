import React, { useContext } from "react";
import {
  Menu,
  MenuItem,
  MenuDivider,
  Icon,
  Popover,
  Tooltip,
  Button,
  Position,
} from "@blueprintjs/core";
import "../cluster.css";
import { useDarkMode } from "@macrostrat/ui-components";
import { mapStyle } from "./macrostrat-map-style";
import { FrameContext } from "~/frame";

export const LayerMenu = ({
  hide,
  mapStyle,
  chooseMapStyle,
  showMarkers,
  toggleShowMarkers,
}) => {
  const { isEnabled } = useDarkMode();

  const { getElement } = useContext(FrameContext);

  const externalMapStyles = getElement("mapStyles")
    ? getElement("mapStyles")
    : [];

  const StandMapMode = isEnabled
    ? "mapbox://styles/mapbox/dark-v10"
    : "mapbox://styles/mapbox/outdoors-v9";

  const mapStyles = [
    { name: "Standard Map", style: StandMapMode },
    {
      name: "Topographic Map",
      style: "mapbox://styles/jczaplewski/cjftzyqhh8o5l2rqu4k68soub",
    },
    { name: "Geologic Map", style: mapStyle },
    ...externalMapStyles,
  ];
  const dropMenu = (
    <Menu>
      {mapStyles.map((styleOb) => {
        const { name, style } = styleOb;
        return (
          <MenuItem
            key={name}
            intent={mapStyle == style ? "primary" : null}
            labelElement={mapStyle == style ? <Icon icon="tick"></Icon> : null}
            text={name}
            onClick={() => {
              chooseMapStyle(style);
            }}
          />
        );
      })}

      <MenuDivider />
      <MenuItem
        label={showMarkers ? "On" : "Off"}
        intent={showMarkers ? "warning" : null}
        onClick={() => toggleShowMarkers()}
        text="Markers"
      />
    </Menu>
  );

  return (
    <div>
      {hide ? null : (
        <div className="mappagemenu">
          <Popover
            content={dropMenu}
            minimal={true}
            position={Position.BOTTOM_LEFT}
          >
            <Tooltip content="Change Map">
              <Button minimal={true}>
                <Icon icon="layers" iconSize={17} />
              </Button>
            </Tooltip>
          </Popover>
        </div>
      )}
    </div>
  );
};
