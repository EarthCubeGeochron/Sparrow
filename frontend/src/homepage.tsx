/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import React, { useState } from "react";
import h from "react-hyperscript";
import { AppNavbar, NavButton } from "app/components/navbar";
import { MapHome } from "./map/index";
import { Frame } from "./frame";
import { InsetText } from "app/layout";
import { Tab, Tabs, Drawer, Button } from "@blueprintjs/core";

import "./styles.modules.css";

const HomePage = () => {
  const [open, setOpen] = useState(false);

  return (
    <div className="homepage">
      <Button onClick={() => setOpen(true)}> </Button>

      <Drawer isOpen={open} title={"Test"} onClose={() => setOpen(false)}>
        <p> Just Testing some stuff out</p>
      </Drawer>
      <InsetText null>
        <Frame id="landingText"></Frame>
        <Frame id="landingGraphic">
          <MapHome></MapHome>
        </Frame>
      </InsetText>
    </div>
  );
};

export { HomePage };
