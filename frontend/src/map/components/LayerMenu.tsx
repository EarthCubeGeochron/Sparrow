import * as React from "react";
import {
  Menu,
  MenuItem,
  MenuDivider,
  Icon,
  Popover,
  Tooltip,
  Button,
  Position,
  InputGroup,
} from "@blueprintjs/core";
import "../cluster.css";
import h from "@macrostrat/hyper";
import { useDarkMode } from "@macrostrat/ui-components";
import { mapStyle } from "../MapStyle";

export const LayerMenu = ({
  hide,
  MapStyle,
  chooseMapStyle,
  //mapstyles,
  showMarkers,
  toggleShowMarkers,
}) => {
  const { isEnabled } = useDarkMode();

  const StandMapMode = isEnabled
    ? "mapbox://styles/mapbox/dark-v10"
    : "mapbox://styles/mapbox/outdoors-v9";

  const mapStyles = [
    { name: "Standard Map", style: StandMapMode },
    {
      name: "Topographic Map",
      style: "mapbox://styles/thefallingduck/cklb8itjb23wr17pd5ukdlne5",
    },
    { name: "Geologic Map", style: mapStyle },
    {
      name: "Satelite Map",
      style: "mapbox://styles/jczaplewski/cjeycrpxy1yv22rqju6tdl9xb",
    },
  ];
  const dropMenu = (
    <Menu>
      {mapStyles.map((styleOb) => {
        const { name, style } = styleOb;
        return (
          <MenuItem
            key={name}
            intent={MapStyle == style ? "primary" : null}
            labelElement={MapStyle == style ? <Icon icon="tick"></Icon> : null}
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
          <Popover content={dropMenu} minimal={true} position={Position.BOTTOM}>
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
