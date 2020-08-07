import React, { useState, useEffect } from "react";
import { Drawer, Button, Card } from "@blueprintjs/core";

export function MapDrawer({ MacroStratData = null, drawOpen, setDrawOpen }) {
  return (
    <div>
      <Drawer isOpen={drawOpen} autoFocus={false} enforceFocus={false}>
        <p>
          This is Where the MacroStrat Data will be Shown for each Spot Picked
          on the Map
        </p>
      </Drawer>
    </div>
  );
}
