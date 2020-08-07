import React from "react";
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

export const LayerMenu = ({
  MapStyle,
  setMapStyle,
  mapstyles,
  showMarkers,
  setShowMarkers,
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
        onClick={() => setMapStyle(mapstyles.initialMapStyle)}
      />
      <MenuItem
        intent={MapStyle == mapstyles.topoMapStyle ? "primary" : null}
        labelElement={
          MapStyle == mapstyles.topoMapStyle ? <Icon icon="tick"></Icon> : null
        }
        text="Topographic"
        onClick={() => setMapStyle(mapstyles.topoMapStyle)}
      />
      <MenuItem
        intent={MapStyle == mapstyles.mapStyle ? "primary" : null}
        labelElement={
          MapStyle == mapstyles.mapStyle ? <Icon icon="tick"></Icon> : null
        }
        onClick={() => setMapStyle(mapstyles.mapStyle)}
        text="Bedrock Geology"
      />
      <MenuItem
        intent={MapStyle == mapstyles.sateliteMapStyle ? "primary" : null}
        labelElement={
          MapStyle == mapstyles.sateliteMapStyle ? (
            <Icon icon="tick"></Icon>
          ) : null
        }
        onClick={() => setMapStyle(mapstyles.sateliteMapStyle)}
        text="Satelite"
      />

      <MenuDivider />
      <MenuItem
        label={showMarkers ? "On" : "Off"}
        intent={showMarkers ? "warning" : null}
        onClick={() => setShowMarkers(!showMarkers)}
        text="Markers"
      />
    </Menu>
  );
  return (
    <Popover content={dropMenu} position={Position.BOTTOM}>
      <Tooltip content="Change Map">
        <Button icon="layers"></Button>
      </Tooltip>
    </Popover>
  );
};
