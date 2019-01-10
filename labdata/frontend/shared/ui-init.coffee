import 'babel-polyfill'
import { FocusStyleManager } from "@blueprintjs/core"
# Turn off accessibility halos by default
FocusStyleManager.onlyShowFocusOnTabs()

# Should import this in styles
import '@blueprintjs/core/lib/css/blueprint.css'
import '@blueprintjs/icons/lib/css/blueprint-icons.css'
import './ui-main.styl'
