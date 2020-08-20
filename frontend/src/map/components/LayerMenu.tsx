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

export const LayerMenu = ({
  hide,
  MapStyle,
  chooseMapStyle,
  mapstyles,
  showMarkers,
  toggleShowMarkers,
}) => {
  const dropMenu = (
    <Menu>
      <MenuItem
        intent={MapStyle == mapstyles.initialMapStyle ? "primary" : null}
        labelElement={
          MapStyle == mapstyles.initialMapStyle ? (
            <Icon icon="tick"></Icon>
          ) : null
        }
        text="Standard Map"
        onClick={() => chooseMapStyle(mapstyles.initialMapStyle)}
      />
      <MenuItem
        intent={MapStyle == mapstyles.topoMapStyle ? "primary" : null}
        labelElement={
          MapStyle == mapstyles.topoMapStyle ? <Icon icon="tick"></Icon> : null
        }
        text="Topographic"
        onClick={() => chooseMapStyle(mapstyles.topoMapStyle)}
      />
      <MenuItem
        intent={MapStyle == mapstyles.mapStyle ? "primary" : null}
        labelElement={
          MapStyle == mapstyles.mapStyle ? <Icon icon="tick"></Icon> : null
        }
        onClick={() => chooseMapStyle(mapstyles.mapStyle)}
        text="Bedrock Geology"
      />
      <MenuItem
        intent={MapStyle == mapstyles.sateliteMapStyle ? "primary" : null}
        labelElement={
          MapStyle == mapstyles.sateliteMapStyle ? (
            <Icon icon="tick"></Icon>
          ) : null
        }
        onClick={() => chooseMapStyle(mapstyles.sateliteMapStyle)}
        text="Satelite"
      />

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
          <Popover content={dropMenu} position={Position.BOTTOM}>
            <Tooltip content="Change Map">
              <Button icon="layers"></Button>
            </Tooltip>
          </Popover>
        </div>
      )}
    </div>
  );
};
